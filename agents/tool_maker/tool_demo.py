# tool_creator assistant
import tool_maker.tool_creator as creator 
from tool_maker.creator_config import AssistantConfig as CreatorConfig 

# tool_user assistant
import tool_maker.tool_user as user
from tool_maker.user_config import AssistantConfig as UserConfig 

if __name__ == '__main__':
    # create the tool creator assistant and chat to create your tools
    creator_details = CreatorConfig().assistant_details
    creator.talk_to_tool_creator(creator_details)

    # create the tool user assistant and chat to test your tools
    user_details = UserConfig().assistant_details
    user.talk_to_tool_user(user_details)
