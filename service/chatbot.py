# Создание Streamlit приложения
import streamlit as st
from config import *
from main import entities, relations
from text_processing import process_text_qwen
from graph_manager import plot_graph, nx

# Инициализация графа
G = nx.DiGraph()

# Функция для заполнения графа
def populate_graph(G, e, level=None):
    if e in G.nodes:
        return
    if e in entities.keys():
        G.add_node(e, label=e)
    if level is not None and level <= 0:
        return
    new_ent = set(
        [r['source'] for r in relations if r['target'] == e] + 
        [r['target'] for r in relations if r['source'] == e]
    )
    for ne in new_ent:
        populate_graph(G, ne, None if level is None else level-1)
    for r in relations:
        if r['source'] == e:
            G.add_edge(e, r['target'], label=r['relation'], desc=r['desc'])
        if r['target'] == e:
            G.add_edge(r['source'], e, label=r['relation'], desc=r['desc'])

# Функция для создания контекста
def create_context(G):
    return '\n'.join(
        e[-1]['desc'] for e in G.edges(data=True)
    )

# Streamlit UI
st.title("Чат-бот на основе графов")

# Ввод вопроса пользователем
q = st.text_input("Введите ваш вопрос:")

# Кнопка для генерации ответа
if st.button("Получить ответ"):
    try:
        # Заполнение графа
        populate_graph(G, "правила_проживания_в_общежитии", 2)

        # Генерация контекста
        context = create_context(G)

        # Обработка вопроса
        question_system_prompt = """
        Ниже в тройных обратных кавычках приводится короткий текст. Тебе необходимо выделить из него все сущности,
        похожие на сущности из списка в двойных кавычках: "{list}". Верни только список сущностей в скобках
        через запятую, например: (Яндекс, компания, директор). Верни только те сущности, которые в явном виде
        присутствуют в запросе. Не придумывай никакие дополнительные сущности и не рассуждай.
        --текст--
        ```
        {}
        ```
        """.replace('{list}',', '.join(entities.keys()))

        user_system_prompt = "Отвечай не придумывая ничего нового от себя. Четко следуй инструкциям основного запроса."

        question_prompt ="""
        Тебе задан следующий запрос от пользователя: {question}.
        Ответь на этот вопрос, используя при этом информацию, содержащуюся ниже в тройных обратных кавычках:
        ```
        {context}
        ```
        """

        # Ответы на основе контекста и вопроса
        ents = process_text_qwen(system_prompt=question_system_prompt, prompt=q)
        ans = process_text_qwen(
            system_prompt=user_system_prompt,
            prompt=question_prompt.replace('{context}', context).replace('{question}', q)
        )

        # Вывод результата
        st.success("Ответ:")
        st.write(ans)
        # st.subheader("Извлечённые сущности:")
        # st.write(ents)

    except Exception as e:
        st.error(f"Произошла ошибка: {e}")
