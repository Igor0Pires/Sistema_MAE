from cloudscraper import create_scraper # biblioteca para contornar proteção de sites que usam Cloudflare
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright # biblioteca para automação de navegadores

import json 
import random
import pickle # biblioteca para salvar e carregar objetos Python em arquivos
import asyncio
import requests

scraper = create_scraper()

urls_courses = ["https://app.datacamp.com/learn/career-tracks/associate-data-engineer-in-sql", "https://app.datacamp.com/learn/career-tracks/associate-data-scientist-in-python"]
urls_skills = ["https://app.datacamp.com/certification/get-started/data-engineer-associate/overview", "https://app.datacamp.com/certification/get-started/associate-data-scientist/overview"]


response = requests.get(urls_courses[0])
print(response.status_code) # erro 403: Forbidden, indica que a requisição foi negada pelo servidor

response = scraper.get(urls_courses[0]) # usando o scraper para contornar a proteção do site
print(response.status_code) # agora deve retornar 200, indicando sucesso

# soup = BeautifulSoup(response.text, "html.parser") # analisa o HTML da página
# print(soup.prettify()) # imprime o HTML formatado 

semaphore = asyncio.Semaphore(5) # Limita o número de páginas abertas simultaneamente para 5

# extrair o conteudo das habilidades de cada trilha
async def extract_skills(context, url):
    async with semaphore:
        page = await context.new_page()
        try: # tenta acessar a página
            await page.goto(url, timeout=60000)
            await asyncio.sleep(random.uniform(2, 4))
            
            if "just a moment" not in (await page.content()).lower(): # Verifica se a página não foi redirecionada para uma página de proteção
                soup = BeautifulSoup(await page.content(), "html.parser") # analisa o HTML da página
                
                skills = list(set([skills.get_text(strip=True) # extrai as habilidades (sem duplicatas)
                        for skills in soup.select("section ul span")])) # (section ul span) é o seletor CSS que localiza as habilidades
                
                track_element = soup.find("h1") # localiza o elemento que contém o nome da trilha
                track = track_element.get_text(strip=True) if track_element else "N/A" # extrai o texto do elemento, se encontrado

                data = []
                for skill in skills:
                    data.append({"track": track, "skill": skill})# cria um dicionário com a trilha e a habilidade
                return data
            
            else:
                print("❌ Falha: Cookies expirados ou inválidos. Repita o login manual.")
                return None
        except Exception as e: # se ocorrer um erro ao acessar a página
            print(f"❌ Erro ao extrair habilidades da página {url}: {e}")
            return None
        finally: # garante que a página será fechada
            await page.close()
            print(f"✅ Página {url} fechada.")

# extrair o conteudo dos cursos de cada trilha
async def extract_courses(context, url):
    async with semaphore:
        page = await context.new_page()
        try:
            await page.goto(url, timeout=60000)
            await asyncio.sleep(random.uniform(2, 4)) # espera um tempo aleatório entre 2 e 4 segundos para evitar bloqueios por parte do site
            
            if "just a moment" not in (await page.content()).lower():
                soup = BeautifulSoup(await page.content(), "html.parser")

                track_element = soup.find("h1")
                track = track_element.get_text(strip=True) if track_element else "N/A"

                projects = {optional.find_parent('div') for optional in soup.select(".mfe-app-learn-hub-1moscjt")} # projetos opcionais do curso o ".mfe-app-learn-hub-1moscjt" é o seletor CSS que localiza os projetos

                courses = list(set([course.get_text(strip=True) for course in soup.select("h3.mfe-app-learn-hub-1yqo1j7") # h3.mfe-app-learn-hub-1yqo1j7 é o seletor CSS que localiza os cursos
                                if course.find_parent('div') not in projects])) # extrai apenas os cursos
                await page.close()
                duration = {}
                try: # tenta acessar a página de cada curso para extrair a duração
                    for course in courses:
                        course_page = course.replace(" ", "-").lower() # formata o nome do curso para criar a URL
                        tmp_url = f"https://app.datacamp.com/learn/courses/{course_page}" 
                        page = await context.new_page() 

                        await page.goto(tmp_url, timeout=60000)
                        await asyncio.sleep(random.uniform(2, 3))

                        soup = BeautifulSoup(await page.content(), "html.parser")

                        duration_element = soup.select_one(".mfe-app-learn-hub-hdd90k")# seletor CSS que localiza a duração do curso
                        duration[course] = duration_element.get_text(strip=True) if duration_element else "N/A"

                        await page.close()

                    print(f"✅ Duração de curso extraídos com sucesso da página {url}.")
                except Exception as e:
                    print(f"❌ Erro ao acessar a página do curso: {e}")
                    return None
                data = []
                for course in courses:
                    data.append({"track": track, "course": course, "duration": duration[course]})
                return data
            else:
                print("❌ Falha: Cookies expirados ou inválidos. Repita o login manual.")
                return None
        except Exception as e:
            print(f"❌ Erro ao extrair curso da página {url}: {e}")
            return None
            
# acessar a página com cookies salvos e fazer o scraping
async def access_with_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
                "--disable-blink-features=AutomationControlled", # Desativa detecção de automação
                "--disable-web-security"  # Ignora políticas CORS (regras de segurança que restringem o acesso a recursos entre diferentes origens)
            ]) # Headless=True para não abrir a janela do navegador, False para abrir a janela do navegador
        
        # Carrega cookies
        try:
            with open("cookies/datacamp_cookies.pkl", "rb") as f:
                cookies = pickle.load(f)# carrega os cookies salvos no arquivo "datacamp_cookies.pkl"
        except:
            print("❌ Erro: Primeiro execute get_cookies.py para salvar os cookies.")
            return
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            bypass_csp=True  # Contorna políticas de segurança
        )
        await context.add_cookies(cookies)# adiciona os cookies ao contexto do navegador

        ## Cria as tarefas para extrair habilidades e cursos
        tasks_skill = [extract_skills(context, url) for url in urls_skills]
        tasks_courses = [extract_courses(context, url) for url in urls_courses]

        ## Executa as tarefas de forma assíncrona
        results_skill = await asyncio.gather(*tasks_skill) 
        results_courses = await asyncio.gather(*tasks_courses)

        # Descompacta os resultados e converte para DataFrame
        results_skill = [item for sublist in results_skill for item in sublist] if results_skill else []
        results_courses = [item for sublist in results_courses for item in sublist] if results_courses else []

        # Cria json com os resultados
        with open("./data/processed/skills.json", "w") as f:
            json.dump(results_skill, f, indent=4)
        print("✅ Habilidades extraídas com sucesso.")
        with open("./data/processed/courses.json", "w") as f:
            json.dump(results_courses, f, indent=4)
        print("✅ Cursos extraídos com sucesso.")

asyncio.run(access_with_cookies()) 
