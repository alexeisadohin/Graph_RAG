from config import *
from algorithms import extract_ER
from graph_manager import create_and_plot_graph

def read_pdf(filepath):
    """Читает PDF файл и возвращает текст.

    Args:
        filepath: Путь к PDF файлу.

    Returns:
        Строку, содержащую весь текст из PDF файла, или None, если произошла ошибка.
    """
    try:
        with open(filepath, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in range(len(pdf_reader.pages)):
                page_obj = pdf_reader.pages[page]
                text += page_obj.extract_text()
            return text
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filepath}' не найден.")
        return None
    except PyPDF2.errors.PdfReadError:
        print(f"Ошибка: Не удалось прочитать PDF файл '{filepath}'. Возможно, он поврежден.")
        return None
    except Exception as e:  # Общий обработчик ошибок для других непредвиденных ситуаций
        print(f"Ошибка при чтении PDF: {e}")
        return None
    

text_input = read_pdf(filepath)

system_prompt = r"""
# Цель
Тебе на вход даётся текстовый документ. Сначала выдели все сущности, которые необходимы, чтобы передать всю содержащуются в тексте информацию и идеи. Далее, найди все связи между этими сущностями в тексте. Также найди связи между обнаруженными сущностями в тексте и контекстом - набор сущностей и связей, котоырй был извлечен в предыдущей итерации работы над другой частью этого текста.

{context}

# Шаги
1. Выдели все сущности. Для каждой найденной сущности, укажи:
- entity_name: Имя сущности, заглавными буквами
- entity_type: Предложи несколько категорий для сущности. Категории не должны быть конкретными, а должны быть наиболее общими. 
- entity_description: Подробное описание атрибутов сущности.
Не используй кавычки и другие знаки препинания в имени сущности. Удаляй лишние кавычки.
Выведи информацию о сущности в следующем виде (entity|<entity_name>|<entity_type>|<entity_description>)

2. Для всех сущностей, выделенных на шаге 1, выдели все связи, т.е. пары (исходная_сущность, целевая_сущность) которые *связаны* между собой.
Для каждой пары связанных сущностей, извлеки следующую информацию:
- source_entity: имя исходной сущности, как она найдена на шаге 1
- target_entity: имя целевой сущности, как она найдена на шаге 1
- relationship_name: короткое имя связи между сущностями
- relationship_description: описание того, как исходная сущность и целевая сущность связаны между собой. В связах могут участвовать только сущности, выделенные на шаге 1. 
 Выведи информацию о связях в следующем виде (relationship|<source_entity>|<target_entity>|<relationship_name>|<relationship_description>)

3. Выведи результат в виде списка, содержащего все сущности, найденные на шаге 1, и связи, найденные на шаге 2. Используй **перевод строки** как разделитель списка.

4. Когда закончишь, выведи [EOF]

######################
-Примеры-
######################
Текст:
Борщ — горячий заправочный суп на основе свёклы, которая придаёт ему характерный красный цвет.
В словаре В. И. Даля — род щей, похлёбка из квашеной свёклы, на говядине и свинине, или со свиным салом. Получило широкое распространение во многих национальных кухнях: это блюдо есть у русских, белорусов и др.
######################
Результат:
(entity|БОРЩ|БЛЮДО|горячий заправочный суп на основе свёклы)
(entity|ГОВЯДИНА|ИНГРЕДИЕНТ|Мясо коровы, входящее в состав борща)
(entity|СВИНИНА|ИНГРЕДИЕНТ|Мясо свиньи, входящее в состав борща)
(entity|ЩИ|БЛЮДО|вид первого блюда)
(entity|РУССКИЕ|НАРОД|проживающие в России)
(entity|БЕЛОРУСЫ|НАРОД|проживающие в Белоруссии)
(relationship|БОРЩ|ЩИ|ЧАСТНЫЙ_СЛУЧАЙ|Борщ является разновидностью Щей)
(relationship|БОРЩ|ГОВЯДИНА|СОДЕРЖИТ|Борщ может содержать говядину)
(relationship|БОРЩ|СВИНИНА|СОДЕРЖИТ|Борщ может содержать свинину)
(relationship|БОРЩ|РУССКИЕ|РАСПРОСТРАНЕНИЕ|Борщ распространён у русских)
(relationship|БОРЩ|БЕЛОРУСЫ|РАСПРОСТРАНЕНИЕ|Борщ распространён у белорусов)
[EOF]
######################
Текст:
Цифровой рубль  — цифровая валюта центрального банка, разрабатываемая Банком России (ЦБ РФ), третья форма российской национальной валюты в дополнение к уже существующим наличной и безналичной формам денег.
Цифровой рубль будет эмитироваться Банком России. Цифровой рубль сочетает в себе свойства наличных и безналичных рублей.
######################
Результат:
(entity|ЦИФРОВОЙ_РУБЛЬ|ВАЛЮТА|цифровая валюта центрального банка)
(entity|БАНК РОССИИ|БАНК|Центральный банк России)
(entity|НАЛИЧНАЯ|ФОРМА ДЕНЕГ|Деньги, распространяемые купюрами)
(entity|БЕЗНАЛИЧНАЯ|ФОРМА ДЕНЕГ|Деньги, распространяемые в электронном виде)
(relationship|ЦИФРОВОЙ РУБЛЬ|БАНК РОССИИ|ЭМИТИРУЕТСЯ|Цифровой рубль будет эмитироваться Банком России)
(relationship|ЦИФРОВОЙ РУБЛЬ|НАЛИЧНАЯ|ИМЕЕТ_СВОЙСТВА|Цифровой рубль имеет свойста наличных денег)
(relationship|ЦИФРОВОЙ РУБЛЬ|БЕЗНАЛИЧНАЯ|ИМЕЕТ_СВОЙСТВА|Цифровой рубль имеет свойста безналичных денег)
######################
-Реальные данные-
######################
Текст: {text}
######################
Результат:
"""


user_prompt = f'''Тебе на вход даётся текстовый документ {text_input}. Сначала выдели все сущности, которые необходимы, чтобы передать всю содержащуются в тексте информацию и идеи. Далее, найди все связи между этими сущностями в тексте.
 Также найди связи между обнаруженными сущностями в тексте и контекстом - набор сущностей и связей, котоырй был извлечен в предыдущей итерации работы над другой частью этого текста.
 Четко следуй системным инструкциям.'''




def process_text_qwen(system_prompt="", prompt = user_prompt): # system_prompt по умолчанию пустая строка
    try:
        # Формирование запроса для Gradio
        result = client.predict(
            query=prompt,
            system=system_prompt,
            radio="72B",
            api_name="/model_chat"
        )

        # Извлекаем ответ и обновляем историю (если нужно)

        response = result[1][0][-1]['text'] # или другой ключ, если структура ответа другая
         

        return response


    except Exception as e:
        print(f"Error with Qwen via Gradio: {e}")
        return None
    


def save_response_to_json(response: str, filename: str, output_dir: str):
    if response is None:
        print(f"Файл {filename} не будет сохранён ввиду пустого запроса.")
        return

    filepath = os.path.join(output_dir, filename)
    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        if "processed" in output_dir:
            json.dump(response, f, ensure_ascii=False, indent=4)
        else:
            json.dump({"model_response": response}, f, ensure_ascii=False, indent=4)

def count_tokens(text):
    return len(ENCODING.encode(text))

def chunk_text(text, max_tokens=MAX_TOKENS):
    tokens = ENCODING.encode(text)
    chunks = []
    current_chunk = []

    for token in tokens:
        current_chunk.append(token)
        if len(ENCODING.decode(current_chunk)) >= max_tokens :
            chunks.append(ENCODING.decode(current_chunk[:-1]))
            current_chunk = [token]


    chunks.append(ENCODING.decode(current_chunk))
    return chunks

def format_context(entities, relations):
    context = "Ранее извлеченные сущности и связи:\n"
    if entities:
        context += "Entities:\n"
        for entity, data in entities.items():
            context += f"- {entity} (Types: {', '.join(data['kind'])})\n"
    if relations:
        context += "Relations:\n"
        for relation in relations:
            context += f"- {relation['source']} --{relation['relation']}--> {relation['target']}\n"
    return context

def process_text_with_context(text_chunks, prompt_template, system_prompt, context_cache=None, intermediate_filename="intermediate_results.json"):
    all_entities = {}
    all_relations = []

    if os.path.exists(intermediate_filename):
        with open(intermediate_filename, "r", encoding="utf-8") as f:
            intermediate_data = json.load(f)
            all_entities = intermediate_data["entities"]
            all_relations = intermediate_data["relations"]
            start_chunk_index = intermediate_data["last_processed_chunk"]
    else:
        start_chunk_index = 0

    for i in tqdm(range(start_chunk_index, len(text_chunks)), desc="Processing chunks", unit="chunk", initial=start_chunk_index, total=len(text_chunks)):
        chunk = text_chunks[i]

        if context_cache:
            cache_key = f"chunk_{i}"
            if cache_key in context_cache:
                context, entities, relations = context_cache[cache_key] # Добавили history в кеш
                all_entities.update(entities)
                all_relations.extend(relations)
                continue

        if i > 0 and not context_cache:
            context = format_context(all_entities, all_relations)
        else:
            context = ""

        prompt = prompt_template.format(text=chunk, context=context)

        response = process_text_qwen(system_prompt, prompt) # Передаем history и system_prompt
        if response:
            lines = response.strip().split('\n')
            entities, relations = extract_ER(lines)
            all_entities.update(entities)
            all_relations.extend(relations)

            if context_cache:
                context_cache[cache_key] = (context, entities, relations) # Сохраняем history в кеш

        intermediate_data = {"entities": all_entities, "relations": all_relations, "last_processed_chunk": i + 1} # Сохраняем историю в промежуточный файл
        with open(intermediate_filename, "w", encoding="utf-8") as f:
            json.dump(intermediate_data, f, ensure_ascii=False, indent=4)

    return all_entities, all_relations


def process_and_save_all(text: str, prompt_template: str, system_prompt: str,context_cache=None):
    raw_dir = "raw_responses"
    processed_dir = "processed_responses"
    graphs_dir = "graphs"

    text_chunks = chunk_text(text)

    entities, relations = process_text_with_context(
        text_chunks, prompt_template, system_prompt, context_cache=context_cache
    )

    response_text = "\n".join(f"(entity|{entity}|{', '.join(data['kind'])}|{'; '.join(data['desc'])})" for entity, data in entities.items()) + "\n" + "\n".join(f"(relation|{rel['source']}|{rel['target']}|{rel['relation']}|{rel['desc']})" for rel in relations)
    save_response_to_json(response_text, "qwen_response.json", raw_dir)  
    processed_data = {"entities": entities, "relations": relations}
    save_response_to_json(processed_data, "qwen_processed.json", processed_dir) 

    create_and_plot_graph(entities, relations, filename="qwen_graph.png", output_dir=graphs_dir) 
