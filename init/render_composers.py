from utils.args import *
from utils.dir import *
from utils.dotenv import *
from utils.compose import *

def main():
    
    args = handle_args()

    create_dev_and_prod_directories()

    generate_dotenv_files(args)

    generate_docker_compose_files(args)

if __name__ == "__main__":
    main()
