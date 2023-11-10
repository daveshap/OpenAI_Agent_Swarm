# env
from dotenv import load_dotenv
load_dotenv()

# tool_user assistant
import tool_maker.tool_user as user
from tool_maker.user_config import AssistantConfig as UserConfig 

if __name__ == '__main__':
    # create the tool user assistant and chat to test your tools
    user_details = UserConfig().assistant_details
    user.talk_to_tool_user(user_details)

