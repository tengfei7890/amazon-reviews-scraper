from core_extract_comments import *
from core_utils import *

def get_reviews(input_product_ids_filename):
    with open(input_product_ids_filename, 'r') as r:
        product_ids = [p.strip() for p in r.readlines()]
        logging.info('{} product ids were found.'.format(len(product_ids)))
        reviews_counter = 0
        for product_id in product_ids:
            _, exist = get_reviews_filename(product_id)
            if exist:
                logging.info('product id [{}] was already fetched. Skipping.'.format(product_id))
                continue
            reviews = get_comments_with_product_id(product_id)
            reviews_counter += len(reviews)
            logging.info('{} reviews found so far.'.format(reviews_counter))
            persist_comment_to_disk(reviews)
            write_to_csv(reviews,product_id)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    get_reviews("list")
