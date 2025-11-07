from PyPDF2 import PdfReader
import pathlib
pdf_path = pathlib.Path('WorkoutPrograms/Legacy_-_Final_Approved_-_Training_PDF_3_.pdf')
reader = PdfReader(str(pdf_path))
text_parts = []
for i, page in enumerate(reader.pages):
    text_parts.append(f"\n\n==== PAGE {i+1} ====\n\n")
    text_parts.append(page.extract_text() or '')
full_text = ''.join(text_parts)
output_path = pathlib.Path('WorkoutPrograms/legacy_program_text.txt')
output_path.write_text(full_text, encoding='utf-8')
print(f"Extracted text to {output_path}")
