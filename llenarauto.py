#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


DEFAULT_URL = "https://jefrabit.github.io/paginaPrueba/"

def build_driver(headless: bool) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(60)
    return driver

def wait_css(driver, sel, timeout=15):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))

def add_task(driver, text: str):
    inp = wait_css(driver, "#taskInput")
    btn = wait_css(driver, "button")  # tu HTML tiene un solo botón
    inp.clear()
    inp.send_keys(text)
    btn.click()
    # pequeña espera para que el <li> aparezca
    WebDriverWait(driver, 5).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#taskList li")) > 0)

def toggle_first_task_completed(driver):
    lis = driver.find_elements(By.CSS_SELECTOR, "#taskList li")
    if not lis:
        return False
    try:
        lis[0].click()  # en tu JS, click al <li> alterna 'completed'
        return True
    except StaleElementReferenceException:
        return False

def delete_second_task(driver):
    lis = driver.find_elements(By.CSS_SELECTOR, "#taskList li")
    if len(lis) < 2:
        return False
    # botón X es el último hijo del li
    try:
        del_btn = lis[1].find_element(By.CSS_SELECTOR, "button.delete")
        del_btn.click()
        return True
    except Exception:
        return False

def count_tasks(driver) -> int:
    return len(driver.find_elements(By.CSS_SELECTOR, "#taskList li"))

def main():
    parser = argparse.ArgumentParser(description="Rellenar To-Do List en GitHub Pages.")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL de la página (por defecto: tu GitHub Pages).")
    parser.add_argument("--tasks", default="Comprar pan;Hacer tarea de compu;Leer 30 min;Hacer ejercicio",
                        help="Tareas separadas por ';'.")
    parser.add_argument("--clear-first", action="store_true", help="Borrar tareas previas (localStorage).")
    parser.add_argument("--headless", action="store_true", help="Ejecutar sin interfaz gráfica.")
    args = parser.parse_args()

    driver = build_driver(headless=args.headless)
    try:
        driver.get(args.url)

        # Espera a que cargue la app
        wait_css(driver, "#taskInput")
        wait_css(driver, "#taskList")

        # Limpia localStorage si se pide
        if args.clear_first:
            driver.execute_script("localStorage.clear(); document.querySelector('#taskList').innerHTML='';")

        # Agregar tareas
        tasks: List[str] = [t.strip() for t in args.tasks.split(";") if t.strip()]
        for t in tasks:
            add_task(driver, t)
            time.sleep(0.2)

        # Marcar la primera como completada y borrar la segunda
        toggled = toggle_first_task_completed(driver)
        deleted = delete_second_task(driver)

        # Contar tareas finales
        total = count_tasks(driver)
        print(f"✅ Tareas agregadas: {len(tasks)}")
        print(f"⚡ Primera tarea marcada como completada: {'sí' if toggled else 'no'}")
        print(f"🗑️ Segunda tarea eliminada: {'sí' if deleted else 'no'}")
        print(f"📦 Total de tareas visibles ahora: {total}")

        # opcional: esperar para que puedas ver el resultado si no es headless
        if not args.headless:
            print("Cierra la ventana para terminar...")
            time.sleep(3)

    except TimeoutException:
        print("❌ No se pudo cargar la página o seleccionar los elementos.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
