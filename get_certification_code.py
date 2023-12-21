import easyocr
import cv2

def ocr(image_file_path):
        '''
        image_file_path : ocr을 적용할 target image 경로 (여기서는 자동 감지 팝업 숫자 이미지에 해당 됨)
        '''
        img = cv2.imread(image_file_path)
        reader = easyocr.Reader(['en', 'ko'], verbose=False)
        certification_number = reader.readtext(img, detail=0, allowlist="0123456789")[0]
        
        return certification_number