"""Bug finder module.

This is an implementation of a search algorithm that will find all 
occurrences of a pattern spread over multiple lines in a text file.
"""

from __future__ import print_function

__version__ = "0.1"
__author__ = "TV"

import re


class Occurrence:
    """Properties of a match for part of a pattern.
    
    Position (line, column) of the occurrence in the text file.
    """
    def __init__(self, line, column, parent):
        # Coordinates of the occurrence
        self.line = line
        self.column = column
        # Link to the PatternPart object of which this is an occurrence
        self.parent = parent

    def follows(self, otherOccurrence):
        """Check whether an occurrence continues a pattern.
        
        Returns True in case the given occurrence follows 
        the current occurrence, i.e. if it starts at the same
        column on the next line.
        """
        return self.line == otherOccurrence.line + 1 and \
            self.column == otherOccurrence.column

 
class PatternPart:
    """Characteristics of a partial pattern.
    
    This object stores information relative to a part of the 
    total pattern (i.e. one line of the total pattern):
    string to be matched and list of occurrences in the 
    given text file.
    """
    def __init__(self, pattern):
        """Set the pattern and compile the corresponding RegEx."""
        self.pattern = pattern
        # Footprint of the pattern: List of indices of the relevant 
        # characters (e.g. for pattern 'ab c de', the footprint
        # would be [0,1,3,4,5], i.e. skipping spaces)
        # Footprint will be used to determine which characters 
        # have already been used in patterns 
        self.patternFootprint = []

        # Find out the pattern's footprint
        self.measureFootprint(self.pattern)

        # Make sure that all original characters are properly escaped
        rawPattern = re.escape(self.pattern)
        # Allow any character instead of spaces in the pattern
        rawPattern = re.sub(r"\\ ", r".", rawPattern)
        # This makes sure that a given character may be used in multiple
        # matches (e.g. 'aa' matches 'aaa' twice)
        rawPatternOverlap = r"(?=(" + rawPattern + r"))"
        self.regex = re.compile(rawPatternOverlap)
        # Initialize the list of occurrences
        self.occurrences = []

    def findOccurrences(self, lineNumber, line):
        """Find occurrences of the pattern in a line of text."""
        for m in self.regex.finditer(line):
            # print m.start(), m.group()
            # Starting counting at col. 1
            columnNumber = m.start() + 1
            self.occurrences.append(Occurrence(lineNumber, columnNumber, self))

    def measureFootprint(self, pattern):
        """Determine the footprint of a pattern."""
        for index, char in enumerate(pattern):
            if char != " ":
                self.patternFootprint.append(index)
                
       
class UsedCharacters:
    """List of characters involved in matched patterns.
    
    Class used to maintain a list of characters belonging to matched
    patterns, so that they are not reused in other, subsequent matches.
    """
    def __init__(self):
        # Initialize the list
        # Data is organized as a dictionary (indexed by line) 
        # of sets (columns corresponding to the characters), 
        # as access is by line, then column
        self.list = {}
        
    def addPosition(self, line, column):
        """Add position to the list of matched characters.""" 
        if line not in self.list:
            self.list[line] = set();
            
        self.list[line].add(column)
        
    def isPositionUsed(self, line, column):
        """Return True in case the given position is in the list."""
        if line in self.list and column in self.list[line]:
            return True
        
        return False
    
    def markUsed(self, occurrence):
        """Keep track of the characters in matched patterns.
        
        Mark characters belonging to patterns matched in the
        landscape, so as to not reuse them in another pattern.
        """  
        for index in occurrence.parent.patternFootprint:
            self.addPosition(occurrence.line, occurrence.column + index)

    def alreadyUsed(self, occurrence):
        """Check status of the characters in the given occurrence.
        
        Return True in case any of the characters in the given 
        occurrence is already involved in any other matched 
        pattern. 
        """
        for index in occurrence.parent.patternFootprint:
            if self.isPositionUsed(occurrence.line, occurrence.column + index):
                return True

        return False
        


class BugFinder:
    """Find multiline patterns (bugs) in a text file (landscape).
    
    Given a text file containing a pattern possibly spanning
    multiple lines, find occurrences of this pattern in a second
    text file. Spaces are ignored in the pattern, and characters 
    belonging to a pattern already matched in the landscape 
    cannot be reused in any further pattern match.
    """
    def __init__(self):
        # The multiline pattern to be matched (one element per line)
        self.pattern = []
        # Flag indicating that the pattern has been properly set
        self.patternSet = False
        # Number of matches for the whole pattern (i.e. all parts)
        self.matches = 0
        # List of sets of pattern parts 
        # (one item per complete pattern found)
        self.matchParts = []
        # Positions of all characters associated to a matched pattern
        self.usedCharacters = UsedCharacters()
        
    def setPattern(self, fileName):
        """Read the pattern from a file."""
        try:
            file = open(fileName, "r")
            # Store the different lines of the pattern
            lineNumber = 1
            for line in file:
                # Remove EOL and trailing blanks 
                # (leading spaces are assumed significant)
                line = line.rstrip()

                patternPart = PatternPart(line)
                self.pattern.append(patternPart)
                lineNumber += 1
            # TODO: Remove n leading spaces if all pattern lines 
            # have at least that many
            
        except:
            raise Exception("Cannot read the pattern file.")
        
        # The pattern has been successfully set
        self.patternSet = True

    def checkPattern(self):
        """Raise an exception in case the pattern was not properly set."""
        # Check that a pattern as been defined
        if not self.patternSet or len(self.pattern) == 0:
            raise Exception("Pattern has not been properly defined.")
        
    def analyzeLandscape(self, fileName):
        """Read the landscape file to find single-line matches.
        
        For each part of the pattern (i.e. for each line), mark 
        position in the landscape file where they occur. These
        individual parts will be put together to form complete
        patterns in detectPattern().
        """
        # This only makes sense in case the pattern has been set
        self.checkPattern()
        
        try:
            with open(fileName) as file:
                lineNumber = 0
                for line in file:
                    lineNumber += 1
                    # Look for parts of the pattern in the current line
                    for patternPart in self.pattern:
                        patternPart.findOccurrences(lineNumber, line)
        except:
            raise Exception("Cannot read the landscape file.")
                 
    def findOccurrenceOfNextPatternPart(self, occurrenceList):
        """Recursive function to assemble pattern parts.
        
        This function attempts to find line n+1 of a pattern to 
        continue after line n has been found. If the recursive calls
        are successful up to the total number of lines in the pattern,
        this is a match.
        """
        # Select the next pattern part
        for patternPart in self.pattern:
            if self.pattern.index(patternPart) < len(occurrenceList):
                continue
            
            for occurrence in patternPart.occurrences:
                # Skip occurrences that have already been used 
                # in another pattern
                if self.usedCharacters.alreadyUsed(occurrence):
                    continue
                
                if occurrence.follows(occurrenceList[-1]):
                    occurrenceList.append(occurrence)
                    
                    self.findOccurrenceOfNextPatternPart(occurrenceList)
                    
                    break
                    
    
    def detectPattern(self):
        """Assemble pattern part matches into the complete pattern.
        
        Check whether each match for a pattern part is followed 
        by matches of the subsequent pattern parts on the consecutive
        lines. 
        """
        self.checkPattern()
        # Loop over all matches for the first part of the pattern
        for patternFirstPart in self.pattern:
            # Check whether matching other parts have been found
            for occurrence in patternFirstPart.occurrences:
                # Skip occurrences that have already been used 
                # in another pattern
                if self.usedCharacters.alreadyUsed(occurrence):
                    continue

                occurrenceList = [occurrence]
                
                # Look recursively for continuation of the pattern
                self.findOccurrenceOfNextPatternPart(occurrenceList)

                if len(occurrenceList) == len(self.pattern):
                    # Success: Matching pattern parts could be found
                    self.matches += 1
                    # Invalidate the occurrences involved in the 
                    # matching pattern so as to avoid reusing them 
                    # in another match
                    for occurrence in occurrenceList:
                        self.usedCharacters.markUsed(occurrence)
                    # Store the properties of the matching pattern 
                    # parts for later use
                    self.matchParts.append(occurrenceList)
            
            # Stop after the first part
            break


def main():
    # Initialize
    bugFinder = BugFinder()
    
    # Input files
    patternFile = "bug.txt"
    landscapeFile = "landscape.txt"
    
    # Read pattern
    bugFinder.setPattern(patternFile)
    
    # Test: This should return 1 match
    #bugFinder.analyzeLandscape(patternFile)
    
    # Analyze landscape
    bugFinder.analyzeLandscape(landscapeFile)
    
    # Piece pattern parts together
    bugFinder.detectPattern()

    # Output results
    print("Number of patterns found: ", bugFinder.matches)


if __name__ == "__main__":
    main()
