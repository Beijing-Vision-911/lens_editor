### 将Lens_editor打包成可以在windows运行的可执行文件(在Windows系统打包)
### 第一步：使用*nuitka*打包
* 安装命令：`pip install nuitka`

### 第二步：需要C编译器配置环境变量
* 1：编译器地址:`https://github.com/brechtsanders/winlibs_mingw/releases/download/11.2.0-14.0.0-9.0.0-msvcrt-r7/winlibs-x86_64-posix-seh-gcc-11.2.0-llvm-14.0.0-mingw-w64msvcrt-9.0.0-r7.zip`

* 2:下载完之后并解压，打开**mingw64**文件夹，找到**bin**文件夹，然后复制地址

* 3:我的电脑-属性-高级系统设置-高级-环境变量

* 4:系统变量，**path**中增加上述复制地址

* 5:C 高速编译器缓存程序ccache地址:`https://github.com/ccache/ccache/releases/download/v4.6/ccache-4.6-windows-32.zip`

* 6:下载完之后并解压，打开**ccache-4.6-windows-32**文件夹,复制地址

* 7:剩下步骤和上述一样

### 第三步 使用命令开始编译打包
1：打包命令:`python -m nuitka --standalone --follow-imports --enable-plugin=pyside6 .\lens_editor\app.py`

2:命令参数解释说明

* 1：--standalone：独立环境，他人拷贝时可以使用

* 2: --follow-imports：打包所有import导入的模块

* 3: --enable-plugin=pyside6：打包可选标准插件pyside6

* 4: .\lens_editor\app.py`: 打包的.py文件路径

3：打包完之后会生成**app.dist**文件和**app.build**文件，在**app.dist**文件下会生成一个**qpp.exe**文件，双击**app.exe**即可运行
