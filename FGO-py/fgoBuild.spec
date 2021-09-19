# -*- mode: python ; coding: utf-8 -*-

# pyinstaller fgoBuild.spec

block_cipher = None

a = Analysis(['fgoGui.py'],
             pathex=[],
             binaries=[],
             datas=[
                 ('fgoImage', 'fgoImage'),
                 ('fgoTeamup.ini', '.'),
                 ('fgoConfig.json', '.'),
                 ('fgoLogs/.gitkeep', 'fgoLogs'),
                 ('../LICENSE','.'),
                 (HOMEPATH+'/airtest/core/android/static', 'airtest/core/android/static')
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='FGO-py',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='FGO-py')
