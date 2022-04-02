
# 使用 TEX 来编写文档的模板

使用步骤：
* 添加或者修改了 tex 文件后
* ./build_latex.sh   : 表示仅仅对更新了的文件的 section 进行编译生成 pdf
* ./build_latex.sh all : 表示对整个 工程文件夹 中的所有的 tex 进行编译生成一个 pdf


# 提交生成一个 commit

./commit.py 会生成一个 commit 

生成的形式 : update --> V 0.2.0.0402 | 002

并且会将版本号 V 0.2.0.0402 更新到 pdf 文件中

