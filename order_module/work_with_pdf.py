from PyPDF2 import PdfReader, PdfWriter


def split_file(filename="file.pdf", output_file="to_send.pdf"):
    """
    Открываем файл. 
    Считываем до тех пор, пока не встретим ключевую строку. 
    Обрезаем файл (перезаписываем только часть до ключевой строки)
    """
    pdf = PdfReader(filename)


    pdf_writer = PdfWriter()
    for page in range(len(pdf.pages)):
        current_page = pdf.pages[page]

        if current_page.extract_text() == "РАЗДЕЛИТЕЛЬНЫЙ ЛИСТ ДЛЯ РАБОТЫ БОТА. НЕ ПЕРЕМЕЩАТЬ И НЕ УДАЛЯТЬ":
            with open(output_file, "wb") as out:
                pdf_writer.write(out)
                print("created", output_file)
            return

        pdf_writer.add_page(page=current_page)#, str(page))


if __name__ == "__main__":
    split_file()