#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf 文件去水印
"""

from itertools import product
import fitz
import os
import unittest

pic_dir = "image/"

class TestUnstamp(unittest.TestCase):

    # pdf 每一页转图片后去水印
    def test_remove_pdf(self):
        pdf = fitz.open("pdf/mobile.pdf")
        total_pages = len(pdf)
        # 判断页码是否超过100页，决定命名规则
        num_digits = 3 if total_pages >= 100 else 2
        for page_num, page in enumerate(pdf, start=1):
            rotate = int(0)
            # 每个尺寸的缩放系数为2，这将为我们生成分辨率提高4倍的图像
            zoom_x, zoom_y = 2, 2
            trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
            pixmap = page.get_pixmap(matrix=trans, alpha=False)
            for pos in product(range(pixmap.width), range(pixmap.height)):
                rgb = pixmap.pixel(pos[0], pos[1])
                if sum(rgb) >= 600:
                    pixmap.set_pixel(pos[0], pos[1], (255, 255, 255))
            # 使用零填充的方式命名图片文件
            image_filename = f"{pic_dir}pdf_split_{page_num:0{num_digits}d}.png"
            pixmap.pil_save(image_filename)
            print(f"第{page_num}页水印去除完成")

    # 去水印的图片，重新合并成 pdf
    def test_pic2pdf(self):
        pdf = fitz.open()
        img_files = sorted(os.listdir(pic_dir), key=lambda x: str(x).split('.')[0])
        for img in img_files:
            if not img.startswith("pdf_split_"):
                continue

            print("合并图片 " + img)
            imgdoc = fitz.open(pic_dir + img)
            pdfbytes = imgdoc.convert_to_pdf()
            imgpdf = fitz.open("pdf", pdfbytes)
            pdf.insert_pdf(imgpdf)
        pdf.save("pdf/unstamp.pdf")
        pdf.close()

if __name__ == "__main__":
    unittest.main()
