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
    
    Position (line, column) in the text file of the occurrence.
    """
    
    def __init__(self, line, column):
        self.line = line
        self.column = column
        self.used = False
        
    def follows(self, otherOccurrence):
        """Check whether an occurrence may be the continuation.
        
        Returns True in case the given occurrence follows 
        the current occurrence, i.e. if it starts at the same
        column on the next line.
        """
        
        return self.line == otherOccurrence.line + 1 and \
            self.column == otherOccurrence.column


class PatternPart:
    """
    """
    def __init__(self, pattern):
        """Set the pattern and compile the corresponding RegEx."""
        self.pattern = pattern

        # Make sure that all original characters are properly escaped
        rawPattern = re.escape(self.pattern)
        # Allow any character instead of spaces in the pattern
        rawPattern = re.sub(r"\\ ", r".", rawPattern)
        self.regex = re.compile(rawPattern)
        # Initialize the list of occurrences
        self.occurrences = []

    def findOccurrences(self, lineNumber, line):
        """Find occurrences of the pattern in a line of text."""
        
        for m in self.regex.finditer(line):
            # print m.start(), m.group()
            # Starting counting at col. 1
            columnNumber = m.start() + 1
            self.occurrences.append(Occurrence(lineNumber, columnNumber))


class BugFinder:
    def __init__(self):
        self.pattern = []
        self.patternSet = False
        # Number of matches for the whole pattern (i.e. all parts)
        self.matches = 0
        # List of sets of pattern parts 
        # (one item per complete pattern found)
        self.matchParts = []
        
    def setPattern(self, fileName):
        try:
            file = open(fileName, "r")
            # Store the different lines of the pattern
            lineNumber = 1
            for line in file:
                # Remove EOL and trailing blanks 
                # (leading spaces are assumed significant)
                line = line.rstrip()
                
#                 # TODO: Comment!
#                 line.encode('string-escape')
#                 
                patternPart = PatternPart(line)
                self.pattern.append(patternPart)
                lineNumber += 1
            # TODO: Remove n leading spaces if all pattern lines 
            # have at least that many
            
        except:
            print("Cannot read the pattern file.")
            
        self.patternSet = True

    def checkPattern(self):
        # Check that a pattern as been defined
        if not self.patternSet or len(self.pattern) == 0:
            # TODO: Error message
            raise
        
    def analyzeLandscape(self, fileName):
        self.checkPattern()
        
        with open(fileName) as file:
            lineNumber = 1
            for line in file:
                # Look for parts of the pattern in the current line
                for patternPart in self.pattern:
                    patternPart.findOccurrences(lineNumber, line)
                lineNumber += 1
                
    def findOccurrenceOfNextPatternPart(self, occurrenceList):
        # Select the next pattern part
        for patternPart in self.pattern:
            if self.pattern.index(patternPart) < len(occurrenceList):
                continue
            
            for occurrence in patternPart.occurrences:
                # Skip occurrences that have already been used 
                # in another pattern
                if occurrence.used:
                    continue
                
                if occurrence.follows(occurrenceList[-1]):
                    occurrenceList.append(occurrence)
                    
                    self.findOccurrenceOfNextPatternPart(occurrenceList)
                    
                    break
                    
    
    def detectPattern(self):
        self.checkPattern()
        # Loop over all matches for the first part of the pattern
        for patternFirstPart in self.pattern:
            # Check whether matching other parts have been found
            for occurrence in patternFirstPart.occurrences:
                # Skip occurrences that have already been used 
                # in another pattern
                if occurrence.used:
                    continue

                occurrenceList = [occurrence]
                
                self.findOccurrenceOfNextPatternPart(occurrenceList)

                if len(occurrenceList) == len(self.pattern):
                    # Success: Matching pattern parts could be found
                    self.matches += 1
                    # Invalidate the occurrences involved in the 
                    # matching pattern so as to avoid reusing them 
                    # in another match
                    for occurrence in occurrenceList:
                        occurrence.used = True
                    # Store the properties of the matching pattern 
                    # parts for later use
                    self.matchParts.append(occurrenceList)
            
            # Stop after the first part
            break


def main():
    # Initialize
    bugFinder = BugFinder()
    
    patternFile = "bug.txt"
    landscapeFile = "landscape.txt"
    
    # Read pattern
    bugFinder.setPattern(patternFile)
    
    # Analyze landscape
    bugFinder.analyzeLandscape(landscapeFile)
#     bugFinder.analyzeLandscape(patternFile)
    
    # Piece pattern parts together
    bugFinder.detectPattern()

    # Output results
    print("Number of patterns found: ", bugFinder.matches)


if __name__ == "__main__":
    main()
