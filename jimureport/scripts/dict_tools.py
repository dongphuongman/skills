#!/usr/bin/env python3
"""
积木报表字典管理工具

用法：
  # 查询字典列表
  python dict_tools.py --action list [--keyword 请假]

  # 创建字典（含字典项，逗号分隔）
  python dict_tools.py --action add --code leave_type --name 请假类型 --items "年假,病假,事假,婚假,产假"

  # 删除字典（连同字典项）
  python dict_tools.py --action delete --code leave_type

  # 查询字典项
  python dict_tools.py --action list-items --code leave_type

  # 新增字典项（追加到已有字典）
  python dict_tools.py --action add-item --code leave_type --items "调休"

  # 删除字典项（按 itemText 匹配）
  python dict_tools.py --action delete-item --code leave_type --items "调休"

  # 编辑字典（修改名称）
  python dict_tools.py --action edit --code leave_type --name 请假类型2

  # 编辑字典项（按 itemText 匹配，修改为新名称，用 -> 分隔）
  python dict_tools.py --action edit-item --code leave_type --items "年假->全薪年假"

环境变量（必须设置）：
  JMREPORT_API   积木报表 API 地址，如 http://192.168.1.x:8085/jmreport
  JMREPORT_TOKEN X-Access-Token
"""

import argparse
import json
import os
import sys
import requests

DEFAULT_API  = os.environ.get("JMREPORT_API",   "<api_base>")
DEFAULT_TOKEN = os.environ.get("JMREPORT_TOKEN", "<token>")


class JmReportDictClient:
    def __init__(self, api_base: str, token: str):
        self.api_base = api_base.rstrip("/")
        self.headers  = {"X-Access-Token": token, "Content-Type": "application/json"}

    def _req(self, method: str, path: str, **kwargs):
        resp = requests.request(method, self.api_base + path, headers=self.headers, **kwargs)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success") and data.get("code") not in (0, 200):
            raise RuntimeError(f"API 错误: {data.get('message', data)}")
        return data.get("result")

    # ── 字典 ──────────────────────────────────────────────────────────────

    def list_dicts(self, keyword: str = "") -> list:
        params = {"pageNo": 1, "pageSize": 100}
        if keyword:
            params["dictName"] = keyword
        result = self._req("GET", "/dict/list", params=params)
        return result.get("records", []) if result else []

    def find_dict(self, code: str) -> dict | None:
        params = {"pageNo": 1, "pageSize": 100, "dictCode": code}
        result = self._req("GET", "/dict/list", params=params)
        records = result.get("records", []) if result else []
        return next((r for r in records if r["dictCode"] == code), None)

    def add_dict(self, code: str, name: str, items: list[str]) -> str:
        """创建字典，返回字典 ID。已存在则直接返回现有 ID。"""
        existing = self.find_dict(code)
        if existing:
            print(f"字典已存在，跳过创建：{code}（ID: {existing['id']}）")
            return existing["id"]

        self._req("POST", "/dict/add", json={
            "dictCode": code, "dictName": name, "description": ""
        })
        d = self.find_dict(code)
        if not d:
            raise RuntimeError("字典创建后查询失败")
        dict_id = d["id"]
        print(f"字典已创建：{name}（{code}，ID: {dict_id}）")

        for idx, text in enumerate(items, start=1):
            self._req("POST", "/dictItem/add", json={
                "dictId": dict_id, "itemText": text.strip(),
                "itemValue": str(idx), "sortOrder": idx, "status": 1
            })
            print(f"  + 字典项：{text.strip()}（值: {idx}）")

        return dict_id

    def delete_dict(self, code: str) -> None:
        d = self.find_dict(code)
        if not d:
            print(f"字典不存在，无需删除：{code}")
            return
        self._req("DELETE", f"/dict/delete?id={d['id']}")
        print(f"字典已删除：{code}（{d['dictName']}）")

    # ── 字典项 ────────────────────────────────────────────────────────────

    def list_items(self, code: str) -> list:
        d = self.find_dict(code)
        if not d:
            raise RuntimeError(f"字典不存在：{code}")
        result = self._req("GET", "/dictItem/list", params={
            "pageNo": 1, "pageSize": 200, "dictId": d["id"]
        })
        return result.get("records", []) if result else []

    def add_items(self, code: str, items: list[str]) -> None:
        d = self.find_dict(code)
        if not d:
            raise RuntimeError(f"字典不存在：{code}")
        existing = self.list_items(code)
        max_val  = max((int(i["itemValue"]) for i in existing if str(i["itemValue"]).isdigit()), default=0)
        max_sort = max((i.get("sortOrder", 0) for i in existing), default=0)
        existing_texts = {i["itemText"] for i in existing}

        for text in items:
            text = text.strip()
            if text in existing_texts:
                print(f"  跳过（已存在）：{text}")
                continue
            max_val  += 1
            max_sort += 1
            self._req("POST", "/dictItem/add", json={
                "dictId": d["id"], "itemText": text,
                "itemValue": str(max_val), "sortOrder": max_sort, "status": 1
            })
            print(f"  + 字典项：{text}（值: {max_val}）")

    def delete_items(self, code: str, items: list[str]) -> None:
        existing = self.list_items(code)
        text_set = {t.strip() for t in items}
        targets  = [i for i in existing if i["itemText"] in text_set]

        if not targets:
            print(f"未找到匹配的字典项：{', '.join(text_set)}")
            return

        ids = ",".join(i["id"] for i in targets)
        self._req("DELETE", f"/dictItem/deleteBatch?ids={ids}")
        for t in targets:
            print(f"  - 字典项已删除：{t['itemText']}（值: {t['itemValue']}）")

    # ── 编辑 ──────────────────────────────────────────────────────────────

    def edit_dict(self, code: str, new_name: str) -> None:
        d = self.find_dict(code)
        if not d:
            raise RuntimeError(f"字典不存在：{code}")
        self._req("POST", "/dict/edit", json={**d, "dictName": new_name})
        print(f"字典已更新：{code}  {d['dictName']} → {new_name}")

    def set_items_status(self, code: str, items: list[str], status: int) -> None:
        """status: 1=启用, 0=禁用"""
        existing = self.list_items(code)
        text_map = {i["itemText"]: i for i in existing}
        label = "启用" if status == 1 else "禁用"
        for text in items:
            text = text.strip()
            item = text_map.get(text)
            if not item:
                print(f"  未找到字典项：{text}")
                continue
            self._req("POST", "/dictItem/edit", json={**item, "status": status})
            print(f"  字典项已{label}：{text}")

    def edit_items(self, code: str, renames: list[str]) -> None:
        """renames 格式：["旧名称->新名称", ...]"""
        existing = self.list_items(code)
        text_map  = {i["itemText"]: i for i in existing}

        for entry in renames:
            if "->" not in entry:
                print(f"  格式错误（需 '旧名称->新名称'）：{entry}")
                continue
            old_text, new_text = [s.strip() for s in entry.split("->", 1)]
            item = text_map.get(old_text)
            if not item:
                print(f"  未找到字典项：{old_text}")
                continue
            self._req("POST", "/dictItem/edit", json={**item, "itemText": new_text})
            print(f"  字典项已更新：{old_text} → {new_text}")


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="积木报表字典管理工具")
    parser.add_argument("--api-base", default=DEFAULT_API,   help="积木报表 API 地址")
    parser.add_argument("--token",    default=DEFAULT_TOKEN, help="X-Access-Token")
    parser.add_argument("--action",   required=True,
                        choices=["list", "add", "edit", "delete", "list-items", "add-item", "edit-item", "delete-item", "enable-item", "disable-item"])
    parser.add_argument("--code",    help="字典编码")
    parser.add_argument("--name",    help="字典名称（仅 add 时需要）")
    parser.add_argument("--items",   help="字典项，逗号分隔（如 '年假,病假,事假'）")
    parser.add_argument("--keyword", help="模糊搜索关键词（仅 list 时使用）")
    args = parser.parse_args()

    client = JmReportDictClient(args.api_base, args.token)

    if args.action == "list":
        dicts = client.list_dicts(args.keyword or "")
        if not dicts:
            print("暂无字典数据")
        else:
            print(f"{'编码':<20} {'名称':<15} ID")
            print("-" * 60)
            for d in dicts:
                print(f"{d['dictCode']:<20} {d['dictName']:<15} {d['id']}")

    elif args.action == "add":
        if not args.code or not args.name:
            parser.error("--code 和 --name 为必填项")
        items = [i for i in (args.items or "").split(",") if i.strip()]
        client.add_dict(args.code, args.name, items)

    elif args.action == "delete":
        if not args.code:
            parser.error("--code 为必填项")
        client.delete_dict(args.code)

    elif args.action == "list-items":
        if not args.code:
            parser.error("--code 为必填项")
        items = client.list_items(args.code)
        if not items:
            print(f"字典 {args.code} 暂无字典项")
        else:
            print(f"{'值':<6} {'名称':<15} 排序")
            print("-" * 35)
            for i in sorted(items, key=lambda x: x.get("sortOrder", 0)):
                print(f"{i['itemValue']:<6} {i['itemText']:<15} {i.get('sortOrder', '-')}")

    elif args.action == "add-item":
        if not args.code or not args.items:
            parser.error("--code 和 --items 为必填项")
        items = [i for i in args.items.split(",") if i.strip()]
        client.add_items(args.code, items)

    elif args.action == "edit":
        if not args.code or not args.name:
            parser.error("--code 和 --name 为必填项")
        client.edit_dict(args.code, args.name)

    elif args.action == "edit-item":
        if not args.code or not args.items:
            parser.error("--code 和 --items 为必填项（格式：'旧名称->新名称'，多个用逗号分隔）")
        renames = [i for i in args.items.split(",") if i.strip()]
        client.edit_items(args.code, renames)

    elif args.action == "enable-item":
        if not args.code or not args.items:
            parser.error("--code 和 --items 为必填项")
        items = [i for i in args.items.split(",") if i.strip()]
        client.set_items_status(args.code, items, 1)

    elif args.action == "disable-item":
        if not args.code or not args.items:
            parser.error("--code 和 --items 为必填项")
        items = [i for i in args.items.split(",") if i.strip()]
        client.set_items_status(args.code, items, 0)

    elif args.action == "delete-item":
        if not args.code or not args.items:
            parser.error("--code 和 --items 为必填项")
        items = [i for i in args.items.split(",") if i.strip()]
        client.delete_items(args.code, items)


if __name__ == "__main__":
    main()
