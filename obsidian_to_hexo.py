import os
import fnmatch
import yaml
import re
import shutil
import argparse
import json

class Obsidian:
    def __init__(self, root):
        self.root = root
        self.attachment_dir = self.get_attachment_dir()

    def __parse_front_matter(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()

        front_matter = []
        if lines:
            if re.match(r'^---', lines[0]):
                lines.pop(0)
                for line in lines:
                    if re.match(r'^---', line):
                        break
                    front_matter.append(line)

        front_matter = "\n".join(front_matter)
        return yaml.safe_load(front_matter)

    def get_attachment_dir(self):
        config_path = os.path.join(self.root, '.obsidian', 'app.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        attachment_folder = config.get('attachmentFolderPath', '')
        return os.path.join(self.root, attachment_folder)

    def find_publishable_markdown_files(self):
        markdown_files = []

        for root, dirs, files in os.walk(self.root):
            if '99-Extras' in dirs:
                dirs.remove('99-Extras')

            for file in files:
                if fnmatch.fnmatch(file, '*.md'):
                    markdown_file = os.path.join(root, file)
                    front_matter = self.__parse_front_matter(markdown_file)
                    if front_matter and front_matter.get('publish') is True:
                        markdown_files.append(markdown_file)

        return markdown_files

class Hexo:
    def __init__(self, root):
        self.root = root
        self.posts_dir = os.path.join(self.root, "source", "_posts")
        self.image_dir = os.path.join(self.root, "source", "images")

class MarkdownProcessor:
    def __init__(self, file):
        self.file = file
        self._image_pattern = r'\!\[.*?\]\((.*?)\)'
        self._ob_image_pattern = r'\!\[\[(.*?)\]\]'

        with open(file, 'r') as f:
            self.content = f.read()

    def parse_images(self):
        img_urls = re.findall(self._image_pattern, self.content)
        ob_img_urls = re.findall(self._ob_image_pattern, self.content)

        return img_urls + ob_img_urls

    def write(self, target_file, new_image_dir):
        updated_content = re.sub(self._image_pattern, fr'![\1]({new_image_dir}/\1)', self.content)
        updated_ob_content = re.sub(self._ob_image_pattern, fr'![\1]({new_image_dir}/\1)', updated_content)

        with open(target_file, 'w') as f:
            f.write(updated_ob_content)

def publish(obsidian_path, hexo_path):
    obsidian = Obsidian(obsidian_path)
    hexo = Hexo(hexo_path)

    markdown_files = obsidian.find_publishable_markdown_files()

    for file in markdown_files:
        filename = os.path.basename(file)
        post_md = os.path.join(hexo.posts_dir, filename)

        print(f"Processing {filename}")
        processor = MarkdownProcessor(file)
        img_urls = processor.parse_images()

        print(f"- copying markdown {filename} to {post_md}")
        processor.write(post_md, '/images')

        for img_url in img_urls:
            img_path = os.path.join(obsidian.attachment_dir, img_url)
            if os.path.exists(img_path):
                img_dest_path = os.path.join(hexo.image_dir, img_url)
                print(f"- copying {img_url} to {img_dest_path}")
                shutil.copyfile(img_path, img_dest_path)
            else:
                print(f"- {img_path} is missing")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transfer Obsidian notes to Hexo blog.')
    parser.add_argument('--obsidian', type=str, required=True, help='Path to the Obsidian vault directory.')
    parser.add_argument('--hexo', type=str, required=True, help='Path to the Hexo project directory.')
    
    args = parser.parse_args()

    obsidian_path = args.obsidian
    hexo_path = args.hexo

    publish(obsidian_path, hexo_path)


