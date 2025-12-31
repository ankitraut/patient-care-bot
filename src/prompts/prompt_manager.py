"""Script implements prompt manager for loading and managing prompts"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Undefined, TemplateError, meta
import frontmatter


class PromptManager:
    _env = None

    @classmethod
    def _get_env(cls, template_dir="templates"):
        template_dir = Path(__file__).parent / template_dir
        if cls._env is None:
            cls._env = Environment(
                loader=FileSystemLoader(template_dir), undefined=Undefined
            )
        return cls._env

    @staticmethod
    def get_prompt(template: str, **kwargs):
        """
        Get a prompt from the template directory and render it with the provided context.
        :param template: The name of the template file (without extension).
        :param kwargs: Context variables to render the template
        :return: Rendered prompt as a string.
        """

        env = PromptManager._get_env()
        template_path = f"{template}.j2"

        with open(env.loader.get_source(env, template_path)[1]) as file:
            post = frontmatter.load(file)

        template = env.from_string(post.content)
        try:
            return template.render(**kwargs)
        except TemplateError as e:
            raise ValueError(f"Error rendering template '{template}': {e}") from e

    @staticmethod
    def get_template_info(template):
        env = PromptManager._get_env()
        template_path = f"{template}.j2"

        with open(env.loader.get_source(env, template_path)[1]) as file:
            post = frontmatter.load(file)

        ast = env.parse(post.content)
        variables = meta.find_undeclared_variables(ast)

        return {
            "name": template,
            "description": post.metadata.get("description", "No Description Provided"),
            "author": post.metadata.get("author", "Unknown Author"),
            "variables": list(variables),
            "frontmatter": post.metadata,
        }
