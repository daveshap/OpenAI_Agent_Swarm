import copy

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from logger import Logger, AgentLogger


class TemplateManager:
    """
    Manage templates.
    """

    def __init__(self, template_dirs=None):
        """
        Initializes the class with the given template directories.

        :param template_dirs: The list of directories to search for templates.
        :type template_dirs: list, optional
        """
        self.log = Logger(self.__class__.__name__)
        self.template_dirs = template_dirs or []
        self.templates = []
        self.templates_env = None

    def load_templates(self):
        """
        Load templates from directories.

        :return: None
        """
        self.log.debug("Loading templates from dirs: %s" % ", ".join(self.template_dirs))
        self.templates_env = Environment(loader=FileSystemLoader(self.template_dirs))
        self.templates = self.templates_env.list_templates() or []

    def get_template(self, template_name):
        """
        Fetches a template.

        :param template_name: The name of the template to fetch
        :type template_name: str
        :return: The fetched template, or None if the template is not found
        :rtype: Template or None
        """
        try:
            template = self.templates_env.get_template(template_name)
        except TemplateNotFound:
            return False, None, f"Template not found: {template_name}"
        return True, template, f"Retrieved template: {template_name}"

    def render_template(self, template_name, variables=None):
        """
        Render a template with variable substitutions.

        :param agent: The associated agent.
        :type agent: object
        :param template_name: The name of the template to render
        :type template_name: str
        :return: A tuple containing a success flag, the rendered message or template name, and a user message
        :rtype: tuple
        """
        variables = variables or {}
        success, template, user_message = self.get_template(template_name)
        if not success:
            return success, template_name, user_message
        try:
            message = template.render(**variables)
            user_message = f"Rendered template: {template_name}"
            self.log.debug(user_message)
            return True, message, user_message
        except Exception as e:
            user_message = f"Error rendering template: {e}"
            self.log.error(user_message)
            return False, None, user_message

    def render_agent_template(self, agent, variables=None):
        agent_log = AgentLogger(agent.name, agent)
        final_variables = vars(agent)
        final_variables.update(variables or {})
        agent_log.debug(f"Rendering template for agent {agent.name}", extra={'variables': final_variables})
        try:
            return self.render_template(agent.instructions, final_variables)
        except Exception as e:
            message = f"Error rendering template for agent {agent.name}: {e}"
            agent_log.error(message)
            return False, None, message
