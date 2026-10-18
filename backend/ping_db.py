from dotenv import load_dotenv
from repository import get_repository
from secrets import token_hex
load_dotenv()
if __name__=='__main__':
    rows=get_repository(token_hex(32)).list()
    print(f'Database connected. {len(rows)} cards found for a new private board.')
