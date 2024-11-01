import pdfplumber
from paddleocr import PaddleOCR
from pdfminer.high_level import extract_text
from PIL import Image
import os
import re
import logging

# 设置日志级别为WARNING，这样就不会显示DEBUG信息
logging.getLogger('ppocr').setLevel(logging.WARNING)
# 初始化PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang="ch")

class PDFOCRProcessor:
    def __init__(self, pdf_file=None):
        self.pdf_file = pdf_file

    def extract_text_from_pdf(self):
        """
        从PDF中提取文字，并返回一个包含PDF所有页面的文本字符串。
        """
        text = extract_text(self.pdf_file)
        return text

    def extract_text_from_image_ocr(self, image_folder='images'):
        """
        从指定文件夹的图片中进行OCR，提取文字，返回包含所有图像OCR结果的字符串。
        """
        ocr_text = ""
        image_files = [f for f in os.listdir(image_folder) if f.endswith('.png')]

        for image_file in image_files:
            image_path = os.path.join(image_folder, image_file)
            ocr_result = ocr.ocr(image_path, cls=True)
            extracted_texts = self.extract_text_from_ocr_results(ocr_result)
            ocr_text += f"{extracted_texts} "

        return ocr_text.strip()

    def extract_text_from_ocr_results(self, ocr_results):
        """
        从OCR结果中提取文字并处理返回。
        """
        extracted_texts = []
        if all(result is None for result in ocr_results):
            return "这个图片未识别出文字"
        else:
            for result in ocr_results:
                for line in result:
                    extracted_texts.append(line[1][0])
        
        return ' '.join(extracted_texts)

    def extract_images(self, output_folder='images'):
        """
        从PDF中提取图像，并保存到指定的文件夹。
        """
        os.makedirs(output_folder, exist_ok=True)
        with pdfplumber.open(self.pdf_file) as pdf:
            for i, page in enumerate(pdf.pages):
                images = page.images
                if images:
                    for img_idx, img in enumerate(images):
                        image = page.within_bbox((img['x0'], img['top'], img['x1'], img['bottom'])).to_image()
                        image_path = os.path.join(output_folder, f'image_page_{i+1}_img_{img_idx+1}.png')
                        image.save(image_path)

    def clean_text(self, text):
        """
        对提取的文本进行清理，去除多余的空格和特殊符号。
        """
        text = re.sub(r'\s+', ' ', text)  # 替换多余的空格为单个空格
        text = re.sub(r'[^\w\s]', '', text)  # 去除特殊符号
        return text.strip()

    def process_pdf_and_images(self):
        """
        提取PDF和图像中的文字，将其整合，并返回清理后的字符串。
        """
        # 从PDF中提取文字
        pdf_text = self.extract_text_from_pdf()
        
        # 提取PDF中的图像
        images_folder = 'images'
        self.extract_images(output_folder=images_folder)
        
        # 对图像进行OCR
        image_text = self.extract_text_from_image_ocr(image_folder=images_folder)
        
        # 合并PDF文字和图像OCR文字
        combined_text = pdf_text + " " + image_text
        
        # 清理并返回结果
        return self.clean_text(combined_text)


# # 使用示例
# pdf_file_path = 'data/翟树泽虚假诉讼再审审查刑事驳回申诉通知书(FBMCLI.C.548712310).pdf'
# processor = PDFOCRProcessor(pdf_file=pdf_file_path)
# combined_text = processor.process_pdf_and_images()
# print(combined_text)
