#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 文件去水印
"""

from itertools import product
import fitz
import os
import unittest

pdf_dir = "pdf/"
output_base_dir = "images/"

class TestUnstamp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the base output directory exists
        if not os.path.exists(output_base_dir):
            os.makedirs(output_base_dir)

    def test_remove_pdf(self):
        # Automatically detect PDF files in the pdf_dir
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_dir, pdf_file)
            pdf = fitz.open(pdf_path)
            total_pages = len(pdf)
            num_digits = 3 if total_pages >= 100 else 2

            # Create a folder named after the PDF file (without extension) in the images directory
            pdf_name = os.path.splitext(pdf_file)[0]
            output_dir = os.path.join(output_base_dir, pdf_name)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            for page_num, page in enumerate(pdf, start=1):
                rotate = 0
                zoom_x, zoom_y = 2, 2
                trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
                pixmap = page.get_pixmap(matrix=trans, alpha=False)

                for x, y in product(range(pixmap.width), range(pixmap.height)):
                    rgb = pixmap.pixel(x, y)
                    if sum(rgb) >= 600:
                        pixmap.set_pixel(x, y, (255, 255, 255))

                image_filename = os.path.join(output_dir, f"{page_num:0{num_digits}d}.png")
                pixmap.save(image_filename)
                print(f"{pdf_file} - 第{page_num}页水印去除完成")

    def test_pic2pdf(self):
        # Automatically detect folders in the images directory
        for root, dirs, files in os.walk(output_base_dir):
            for dir_name in dirs:
                pdf_name = dir_name
                pdf = fitz.open()
                img_dir = os.path.join(root, dir_name)
                img_files = sorted([f for f in os.listdir(img_dir) if f.endswith(".png")], key=lambda x: int(os.path.splitext(x)[0]))

                for img in img_files:
                    img_path = os.path.join(img_dir, img)
                    imgdoc = fitz.open(img_path)
                    pdfbytes = imgdoc.convert_to_pdf()
                    imgpdf = fitz.open("pdf", pdfbytes)
                    pdf.insert_pdf(imgpdf)
                    print(f"合并图片 {img}")

                unstamped_pdf_path = os.path.join(pdf_dir, f"{pdf_name}_unstamp.pdf")
                pdf.save(unstamped_pdf_path)
                pdf.close()

if __name__ == "__main__":
    unittest.main()
