Cur_Dir=$(cd "$(dirname "$0")"; pwd) 
echo $Cur_Dir/flush_blog_content.py
python $Cur_Dir/flush_blog_content.py
python $Cur_Dir/flush_home_page_blog.py
python $Cur_Dir/flush_hot_category.py
python $Cur_Dir/flush_home_page_blog_index.py
python $Cur_Dir/flush_hot_blog.py
