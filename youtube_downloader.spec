# youtube_downloader.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['youtube_downloader.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=['yt_dlp.extractor', 'yt_dlp.utils', 'yt_dlp.postprocessor'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
             
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='YouTube Downloader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='youtube.ico')  # Add your own icon file if you have one