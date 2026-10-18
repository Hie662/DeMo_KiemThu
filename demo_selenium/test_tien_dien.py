"""
Demo Selenium WebDriver: kiem thu chuc nang "Tinh tien dien"
(Module 6 - Bai 1, de bai tinh tien dien o Module 2 - Bai 8)

Cach chay:
    pip install selenium
    python test_tien_dien.py              # mo trinh duyet that de demo
    python test_tien_dien.py --headless   # chay an (khong hien cua so)
    python test_tien_dien.py --slow       # chay cham de demo cho co xem
    python test_tien_dien.py --trang=tinh_tien_dien_loi.html
                                          # chay tren ban co loi co y (de thay FAIL)
"""
import csv
import sys
import time
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

THU_MUC = Path(__file__).resolve().parent
TEN_TRANG = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--trang=")),
                 "tinh_tien_dien.html")
TRANG_WEB = (THU_MUC / TEN_TRANG).as_uri()
FILE_CSV = THU_MUC / "testcases.csv"
THU_MUC_ANH = THU_MUC / "screenshots"
CHAM_LAI = "--slow" in sys.argv          # them --slow de demo cham cho co xem


def tao_trinh_duyet():
    tuy_chon = webdriver.ChromeOptions()
    if "--headless" in sys.argv:
        tuy_chon.add_argument("--headless=new")
    if "--no-sandbox" in sys.argv:
        tuy_chon.add_argument("--no-sandbox")
    tuy_chon.add_argument("--window-size=720,560")
    # Selenium Manager (Selenium >= 4.6) tu tai chromedriver phu hop
    return webdriver.Chrome(options=tuy_chon)


def chay_mot_test_case(driver, tc):
    driver.get(TRANG_WEB)

    o_so_cu = driver.find_element(By.ID, "so_cu")
    o_so_moi = driver.find_element(By.ID, "so_moi")
    o_thanh_tien = driver.find_element(By.ID, "thanh_tien")

    o_so_cu.clear()
    o_so_cu.send_keys(tc["so_cu"])
    o_so_moi.clear()
    o_so_moi.send_keys(tc["so_moi"])
    if CHAM_LAI:
        time.sleep(0.8)

    driver.find_element(By.ID, "btn_tinh").click()

    # Cho (explicit wait) den khi o ket qua co du lieu, khong dung sleep co dinh
    WebDriverWait(driver, 5).until(lambda d: o_thanh_tien.get_attribute("value") != "")
    thuc_te = o_thanh_tien.get_attribute("value")
    if CHAM_LAI:
        time.sleep(0.8)
    return thuc_te


def ket_qua_khop(thuc_te, mong_doi):
    # Trang web làm tròn tiền đến đồng; CSV có thể ghi kết quả chưa làm tròn.
    mong_doi_lam_tron = Decimal(mong_doi).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return Decimal(thuc_te) == mong_doi_lam_tron


def main():
    THU_MUC_ANH.mkdir(exist_ok=True)
    with open(FILE_CSV, encoding="utf-8", newline="") as f:
        danh_sach = list(csv.DictReader(f))

    driver = tao_trinh_duyet()
    ket_qua = []
    try:
        for tc in danh_sach:
            thuc_te = chay_mot_test_case(driver, tc)
            dat = ket_qua_khop(thuc_te, tc["ket_qua_mong_doi"])
            ket_qua.append((tc["ma_tc"], tc["ket_qua_mong_doi"], thuc_te, dat))
            driver.save_screenshot(str(THU_MUC_ANH / f"{tc['ma_tc']}.png"))
    finally:
        driver.quit()

    print(f"{'Ma TC':<6} {'Mong doi':>14} {'Thuc te':>10}  Ket qua")
    print("-" * 44)
    for ma, mong_doi, thuc_te, dat in ket_qua:
        print(f"{ma:<6} {mong_doi:>14} {thuc_te:>10}  {'PASS' if dat else 'FAIL'}")
    so_dat = sum(1 for r in ket_qua if r[3])
    print("-" * 44)
    print(f"Tong: {len(ket_qua)} test case | PASS: {so_dat} | FAIL: {len(ket_qua) - so_dat}")
    sys.exit(0 if so_dat == len(ket_qua) else 1)


if __name__ == "__main__":
    main()
