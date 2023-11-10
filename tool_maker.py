# env
from dotenv import load_dotenv
load_dotenv()

# tool_creator assistant
import tool_maker.tool_creator as creator 
from tool_maker.creator_config import AssistantConfig as CreatorConfig 

if __name__ == '__main__':
    # create the tool creator assistant and chat to create your tools
    creator_details = CreatorConfig().assistant_details
    creator.talk_to_tool_creator(creator_details)
