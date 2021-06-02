# -*- coding: utf-8 -*-
import base64
from io import BytesIO
from PIL import Image
from qrmaker import theqrmodule
import os


def run(data: str, version: int = 1, level: str = 'H',
        picture: str = None, colorized: bool = False,
        contrast: float = 1.0, brightness: float = 1.0, 
        save_name: str = None, save_dir: str = os.getcwd(),
        only_base64: bool = False
) -> tuple:

    supported_chars = r"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ··,.:;+-*/\~!@#$%^&`'=<>[]()?_{}|"

    if not isinstance(data, str) or any(i not in supported_chars for i in data):
        raise ValueError(
            'Wrong data! Make sure the characters are supported!')
    # if not isinstance(version, int) or version not in range(1, 41):
    #     raise ValueError(
    #         'Wrong version! Please choose a int-type value from 1 to 40!')
    # if not isinstance(level, str) or len(level) > 1 or level not in 'LMQH':
    #     raise ValueError(
    #         "Wrong level! Please choose a str-type level from {'L','M','Q','H'}!")
    # if picture:
    #     if not isinstance(picture, str) or not os.path.isfile(picture) or picture[-4:] not in ('.jpg', '.png', '.bmp'):
    #         raise ValueError(
    #             "Wrong picture! Input a filename that exists and be tailed with one of {'.jpg', '.png', '.bmp'}!")
    #     if not isinstance(colorized, bool):
    #         raise ValueError('Wrong colorized! Input a bool-type value!')
    #     if not isinstance(contrast, float):
    #         raise ValueError('Wrong contrast! Input a float-type value!')
    #     if not isinstance(brightness, float):
    #         raise ValueError('Wrong brightness! Input a float-type value!')
    # if save_name and (not isinstance(save_name, str) or save_name[-4:] not in ('.jpg', '.png', '.bmp')):
    #     raise ValueError(
    #         "Wrong save_name! Input a filename tailed with one of {'.jpg', '.png', '.bmp'}!")
    # if not os.path.isdir(save_dir):
    #     raise ValueError('Wrong save_dir! Input a existing-directory!')

    def combine(ver: int, qr_name: str, bg_name: str,
                colorized: bool, contrast, brightness: float,
                save_dir: str, save_name:str = None,
                only_base64: bool = False
    ) -> tuple:
        from qrmaker.constant import alig_location
        from PIL import ImageEnhance, ImageFilter

        qr = Image.open(qr_name)
        qr = qr.convert('RGBA') if colorized else qr

        bg0 = Image.open(bg_name).convert('RGBA')
        bg0 = ImageEnhance.Contrast(bg0).enhance(contrast)
        bg0 = ImageEnhance.Brightness(bg0).enhance(brightness)

        if bg0.size[0] < bg0.size[1]:
            bg0 = bg0.resize(
                (qr.size[0] - 24, (qr.size[0] - 24) * int(bg0.size[1] / bg0.size[0]))
            )
        else:
            bg0 = bg0.resize(
                ((qr.size[1] - 24) * int(bg0.size[0] / bg0.size[1]), qr.size[1] - 24)
            )

        bg = bg0 if colorized else bg0.convert('1')

        aligs = []
        if ver > 1:
            aloc = alig_location[ver-2]
            for a in range(len(aloc)):
                for b in range(len(aloc)):
                    if not ((a == b == 0) or (a == len(aloc)-1 and b == 0) or (a == 0 and b == len(aloc)-1)):
                        for i in range(3*(aloc[a]-2), 3*(aloc[a]+3)):
                            for j in range(3*(aloc[b]-2), 3*(aloc[b]+3)):
                                aligs.append((i, j))

        for i in range(qr.size[0]-24):
            for j in range(qr.size[1]-24):
                if not ((i in (18, 19, 20)) or (j in (18, 19, 20)) or (i < 24 and j < 24) or (i < 24 and j > qr.size[1]-49) or (i > qr.size[0]-49 and j < 24) or ((i, j) in aligs) or (i % 3 == 1 and j % 3 == 1) or (bg0.getpixel((i, j))[3] == 0)):
                    qr.putpixel((i+12, j+12), bg.getpixel((i, j)))

        qr_name = os.path.join(save_dir, os.path.splitext(os.path.basename(bg_name))[
                               0] + '_qrcode.png') if not save_name else os.path.join(save_dir, save_name)
        qr.resize((qr.size[0]*3, qr.size[1]*3))
        
        # convert picture to base64
        buffered = BytesIO()
        qr.save(buffered, format=f"{qr_name[-3:]}")
        qr_base64 = base64.b64encode(buffered.getvalue())
        
        if not only_base64:
            qr.save(qr_name)
        else:
            qr_name = None
        return qr_name, qr_base64

    tempdir = os.path.join(os.path.expanduser('~'), '.myqr')

    try:
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)

        ver, qr_name = theqrmodule.get_qrcode(version, level, data, tempdir)

        if picture:
            qr_name, qr_base64 = combine(
                ver,
                qr_name,
                picture,
                colorized,
                contrast,
                brightness,
                save_dir,
                save_name,
                only_base64
            )
        elif qr_name:
            qr = Image.open(qr_name)
            qr_name = os.path.join(
                save_dir,
                os.path.basename(qr_name)
            ) if not save_name else os.path.join(save_dir, save_name)
            qr.resize((qr.size[0]*3, qr.size[1]*3))
            
            # convert picture to base64
            buffered = BytesIO()
            qr.save(buffered, format=f"{qr_name[-3:]}")
            qr_base64 = base64.b64encode(buffered.getvalue())
            
            if not only_base64:
                qr.save(qr_name)
            else:
                qr_name = None
        return qr_name, qr_base64

    except:
        raise
    finally:
        import shutil
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)


if __name__ == '__main__':
    qr_name, qr_base64 = run(
        data='https://qr.nspk.ru/AD10002OGDBO5NN39VU8JIAE6U5L1UV5?type=02&bank=100000000001&sum=10000&cur=RUB&crc=6FBA',
        version=1,
        level='H',
        picture='logo.png',
        colorized=True,
        contrast=1.0,
        brightness=1.0,
        save_name='result.png',
        save_dir=os.getcwd(),
        only_base64=True
    )
    print(qr_name, qr_base64, sep='\n')
    