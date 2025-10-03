@manual
Feature: Documentation Quality Inspection
As a Quality Assurance Engineer
I want to verify the compliance and content of core product documentation
So that users receive accurate, complete, and legally compliant guides.

Background:
# Setup for the inspection environment, assuming access to required tools and current specs
Given the current required Optimization Notice revision is "#20110804"
And the product release date is 2024
And the required compliance level for this release is "<level>"

Scenario Outline: Comprehensive Document Content and Legal Inspection
When I inspect the document "<document>" located at "<filepath>"

# --- Content and Technical Checks ---
Then the Optimization notice revision is verified to be consistent across all documents
And I scan the document for broken links using a link checker tool
And the tool reports no broken links were found

# --- Guide Content Inspection ---
And the document title is correct and includes the proper product name
And the document contains no grammatical errors, typos, or ambiguous information
And the content is complete, without missing information required by PRDs or IRDs (e.g., What's New, OS Support Matrix)
And the document exists and is not empty, with a manageable file size

# --- Legal Compliance Checks ---
And the proper FTC, privacy compliant notice is available
And the Copyright notice with the correct timestamp appears at the end
And the approved company logo is used in the document

# --- Localization and Metadata Checks ---
And if applicable, the document is located in the correct localization folder, such as "<language_folder>"
And the Copyright notice is in the format "Copyright c [year], ABCDEF Corporation. All rights reserved"
And the document metadata fields (Author, Title, Subject, Key Words) are relevant and free from destructive information
And document printing is allowed

Examples: 
  | document   			  | level | filepath                          | language_folder                 |
  | User Guide 			  | light | Documentation/en_US/UserGuide.pdf | INSTALL_DIR/Documentation/en_US |
  | INSTALL               | light | Documentation/en_US/INSTALL.txt   | INSTALL_DIR/Documentation/en_US |
  | README                | light | Documentation/en_US/README.md     | INSTALL_DIR/Documentation/en_US |
  | User Guide (Japanese) | light | Documentation/ja_JP/UserGuide.pdf | INSTALL_DIR/Documentation/ja_JP |
