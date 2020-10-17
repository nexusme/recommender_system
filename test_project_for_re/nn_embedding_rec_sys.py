# 使用神经网络嵌入构建推荐系统
import json
from itertools import chain
from IPython.core.interactiveshell import InteractiveShell
from collections import Counter, OrderedDict


def data_fetch():
    # Set shell to show all lines of output
    InteractiveShell.ast_node_interactivity = 'all'

    books = []

    with open('files_are_not_here/found_books_filtered.ndjson.json', 'r') as fin:
        # Append each line to the books
        books = [json.loads(lines) for lines in fin]

    # Remove non-book articles
    books_with_wiki = [book for book in books if 'Wikipedia:' in book[0]]
    books_with_no_wiki = [book for book in books if 'Wikipedia:' not in book[0]]
    # print(f'Found {len(books_with_wiki)} books.')
    # for row in books_with_wiki:
    #     print(row[0])

    return books


def map_books_to_int(data):
    book_ind = {book[0]: idx for idx, book in enumerate(data)}
    # for row in book_index:
    #     print(row)
    ind_book = {idx: book for book, idx in book_ind.items()}
    # for row in index_book:
    #     print(row)
    return book_ind, ind_book


def exploring_link(data, index):
    wiki_links = list(chain(*[book[2] for book in data]))
    # print(f"There are {len(set(wiki_links))} unique wikilinks.")
    wikilinks_other_books = [link for link in wiki_links if link in index.keys()]
    # print(f"There are {len(set(wikilinks_other_books))} unique wikilinks to other books.")


def count_items(data):
    """Return ordered dictionary of counts of objects in `data`"""
    # Create a counter object
    counts = Counter(data)
    # Sort by highest count first and place in ordered dictionary
    counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    counts = OrderedDict(counts)
    return counts


def remove(links, links_count):
    to_remove = ['hardcover', 'paperback', 'hardback', 'e-book', 'wikipedia:wikiproject books',
                 'wikipedia:wikiproject novels']
    for t in to_remove:
        links.remove(t)
        _ = links_count.pop(t)
    # Limit to greater than 3 links
    links = [t[0] for t in links_count.items() if t[1] >= 4]
    print(len(links))
    return links


def most_linked_to_books(data):
    # Find set of book wiki links for each book
    unique_wiki_links_books = list(
        chain(*[list(set(link for link in book[2] if link in book_index.keys())) for book in data]))

    # Count the number of books linked to by other books
    wiki_link_book_counts = count_items(unique_wiki_links_books)
    result = list(wiki_link_book_counts.items())[:10]
    print(result)
    return result


def wiki_links_to_index(links):
    link_index = {link: idx for idx, link in enumerate(links)}
    index_link = {idx: link for link, idx in link_index.items()}
    # print(link_index['the economist'])
    # print(index_link[301])
    print(f'There are {len(link_index)} wikilinks that will be used.')


if __name__ == '__main__':
    books_data = data_fetch()
    book_index, index_book = map_books_to_int(books_data)
    exploring_link(books_data, book_index)

    # Find set of wiki links for each book and convert to a flattened list
    unique_wiki_links = list(chain(*[list(set(book[2])) for book in books_data]))
    # wiki_link_counts = count_items(unique_wiki_links)
    # print(list(wiki_link_counts.items())[:10])
    wiki_links = [link.lower() for link in unique_wiki_links]
    # print(f"There are {len(set(wiki_links))} unique wikilinks.")
    wiki_link_counts = count_items(wiki_links)
    # print(list(wiki_link_counts.items())[:10])
    link_removed = remove(wiki_links, wiki_link_counts)
    # link_most = most_linked_to_books(books_data)
    wiki_links_to_index(link_removed)
