# -*- mode: python -*-

block_cipher = None


a = Analysis(['Get_ICM_Data V6.py'],
             pathex=['E:\\workspace\\Get_ICM_Data\\ICM'],
             binaries=None,
             datas=None,
             hiddenimports=['queue'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Get_ICM_Data V6',
          debug=False,
          strip=False,
          upx=True,
          console=True )
