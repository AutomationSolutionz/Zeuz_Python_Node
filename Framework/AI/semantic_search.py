from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from toolz import pipe
from typing import Literal
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cdist
import numpy as np
import time


# TODO: Model loading should go into an init() function which should be called explicitly.

# Load the model
# model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def cleanup_whitespaces(s: str) -> str:
    import re
    return re.sub(r"\s+", ' ', s)


def get_text_excluding_children(driver, element: WebElement) -> str:
    text = driver.execute_script("""
        const parent = arguments[0];
        const childNodes = parent.childNodes;
        let text = '';
        for (let i = 0; i < childNodes.length; i++) {
            if (childNodes[i].nodeType === Node.TEXT_NODE) {
                text += childNodes[i].nodeValue.trim();
            }
        }
        return text;
    """, element)

    return text


def recur_children(driver, root: WebElement):
    child_info: list[dict[str, str]] = []
    tag_skip_list = (
        "script",
        "style",
        "hr",
    )

    find_children_total_time = 0

    def inner(element: WebElement):
        nonlocal find_children_total_time
        tag_name = element.tag_name
        if tag_name in tag_skip_list:
            return

        # Collect information about the current element
        text = get_text_excluding_children(driver, element)
        text = cleanup_whitespaces(text)

        info = {
            "text": text,
            "accessible_name": element.accessible_name,
            "tag": tag_name,
            "is_selected": element.is_selected(),
            "is_enabled": element.is_enabled(),
        }

        attributes = element.get_property("attributes")
        for attr in attributes: # type: ignore
            info[attr["name"]] = attr["value"]

        # Add the WebElement 
        info["element"] = element

        child_info.append(info)

        find_elem_st = time.perf_counter()
        children = element.find_elements(by=By.XPATH, value="./*")
        # children = element.find_elements(by=By.CSS_SELECTOR, value="*")
        find_children_total_time += time.perf_counter() - find_elem_st
        for child in children:
            inner(child)

    inner(root)
    print(f"Total time taken to find child elements: {find_children_total_time:.2f}")
    return child_info


def find_by_semantic_search(driver, query, root_element = None, k = 3) -> list:
    if root_element is None:
        # Find the parent element
        parent_id = r'/html/body'
        parent_element = driver.find_element(by=By.XPATH, value=parent_id)
    else:
        parent_element = root_element

    start_time = time.perf_counter()
    elements_list = recur_children(driver, parent_element)
    print(f"[AI] Time taken to recursively go through all children: {time.perf_counter() - start_time:.2f}")

    exclude_keys = (
        "element",
        "is_enabled",
        "is_selected",
        # "class",
    )

    filterd_list: list[str] = []
    for item in elements_list:
        str_representation = ""
        for key in item:
            if key in exclude_keys:
                continue
            str_representation = f"{str_representation} {item[key]}".strip().lower()
        filterd_list.append(cleanup_whitespaces(str_representation))

    # Build embeddings for the html
    start_time = time.perf_counter()
    html_embeddings = model.encode(filterd_list)
    print(f"[AI] Time taken to build HTML embeddings: {time.perf_counter() - start_time:.2f}")

    def semantic_search_top_k_elements(query: str, k: int = 5):
        user_query = pipe(
            query,
            cleanup_whitespaces,
        )
        user_query_embedding = model.encode([user_query])

        similarity_scores = 1 - cdist(html_embeddings, user_query_embedding, metric="cosine") 
        top_similarities = np.argsort(-similarity_scores, axis=None)[:k]
        top_similarity_indices = np.unravel_index(top_similarities, similarity_scores.shape)

        # print("Top 5 similar indices:", top_similarity_indices[0])

        results: list[dict[Literal["elem", "score"], str]] = []

        # Print the top 5 most similar pairs
        for i in top_similarity_indices[0]:
            results.append({
                "score": similarity_scores[i][0],
                "elem": elements_list[i],
            })

        return results


    start_time = time.perf_counter()
    result = semantic_search_top_k_elements(
        query=query,
        k=k,
    )
    print(f"[AI] Time taken to perform actual semantic search: {time.perf_counter() - start_time:.2f}")
    return result
