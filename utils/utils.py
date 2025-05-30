import re
import os
from pathlib import Path
from typing import Union, Optional, Tuple

from PIL import ImageTk
from PIL.Image import open as pil_open


class Utils:
    @staticmethod
    def get_photo_image_from_source_file(
            source: Union[str, Path],
            size: Optional[Tuple[int, int]] = None
    ) -> ImageTk.PhotoImage | None:
        """
        Загружает изображение с опциональным ресайзом.
        Args:
            source: Путь к файлу с изображением, ИЛИ переменная окружения с путем к файлу
            size: None - без ресайза, (width, height) - с ресайзом
        Returns:
            PhotoImage объект
        """
        if isinstance(source, Path) or os.path.exists(source):
            image_path = str(source)
        else:
            image_path = os.getenv(source)
            if not image_path:
                return None

        _image = pil_open(image_path)
        if size:
            _image.resize(size)
        return ImageTk.PhotoImage(_image)


    @staticmethod
    def to_number(value):
        """Проверка, является ли значение числом"""
        if re.match(r"^\d+?\.\d+?$", value) is None:
            return value.isdigit()
        return True