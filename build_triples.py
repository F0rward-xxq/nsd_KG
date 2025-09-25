# -*- coding: utf-8 -*-
import argparse
import csv
import json
import os
from typing import Dict, List, Tuple, Set


def read_json(path: str) -> List[Dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def disease_node_id(disease_id: str) -> str:
    return f"Disease:{disease_id}"


def build_graph(records: List[Dict]) -> Tuple[List[Dict], List[Tuple[str, str, str]]]:
    nodes: Dict[str, Dict] = {}
    edges_set: Set[Tuple[str, str, str]] = set()  # (start_id, rel_type, end_id)

    # 先建立疾病名到节点ID的映射，用于并发症指向其他疾病时建立关系
    name_to_id: Dict[str, str] = {}
    for rec in records:
        did = str(rec.get('disease_id') or '').strip()
        name = (rec.get('name') or '').strip()
        if not did or not name:
            continue
        name_to_id[name] = disease_node_id(did)

    for rec in records:
        did = str(rec.get('disease_id') or '').strip()
        name = (rec.get('name') or '').strip()
        if not did or not name:
            continue
        nid = disease_node_id(did)

        # properties from content（仅疾病节点，不再创建并发症节点）
        content = rec.get('content') if isinstance(rec.get('content'), dict) else {}
        node_props = {
            'id:ID': nid,
            'name': name,
            ':LABEL': 'Disease',
            'entry_url': (rec.get('source') or {}).get('entry_url', ''),
            'overview': content.get('overview', ''),
            'cause': content.get('cause', ''),
            'prevent': content.get('prevent', ''),
            'symptom': content.get('symptom', ''),
            'inspect': content.get('inspect', ''),
            'diagnosis': content.get('diagnosis', ''),
            'treat': content.get('treat', ''),
            'nursing': content.get('nursing', ''),
            'food': content.get('food', ''),
        }
        nodes[nid] = node_props

        # 若基本知识中“并发症”包含另一个已收录疾病名称，则建立疾病间并发关系
        basic_info = content.get('basic_info') if isinstance(content, dict) else None
        if isinstance(basic_info, dict):
            comps = basic_info.get('并发症')
            comp_list: List[str] = []
            if isinstance(comps, list):
                comp_list = [x for x in comps if isinstance(x, str) and x.strip()]
            elif isinstance(comps, str):
                comp_list = [x.strip() for x in comps.replace('、', ' ').replace(',', ' ').split() if x.strip()]

            for comp_name in comp_list:
                target_id = name_to_id.get(comp_name)
                if target_id and target_id != nid:
                    edges_set.add((nid, 'COMORBID_WITH', target_id))

    return list(nodes.values()), list(edges_set)


def write_neo4j_csv(nodes: List[Dict], edges: List[Tuple[str, str, str]], nodes_path: str, rels_path: str) -> None:
    ensure_dir(nodes_path)
    ensure_dir(rels_path)

    # Nodes CSV
    # Collect all keys to keep header stable
    all_keys: Set[str] = set()
    for n in nodes:
        all_keys.update(n.keys())
    # ensure mandatory headers
    mandatory = ['id:ID', 'name', ':LABEL']
    for m in mandatory:
        all_keys.add(m)
    # order header: mandatory first, then others sorted
    other_keys = sorted(k for k in all_keys if k not in mandatory)
    header = mandatory + other_keys

    with open(nodes_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for n in nodes:
            writer.writerow({k: n.get(k, '') for k in header})

    # Relationships CSV
    with open(rels_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow([':START_ID', ':END_ID', ':TYPE'])
        for s, r, e in edges:
            writer.writerow([s, e, r])


def write_triples_jsonl(records: List[Dict], triples_path: str) -> None:
    ensure_dir(triples_path)
    # 构建 name->id 映射用于并发症匹配
    name_to_id: Dict[str, str] = {}
    for rec in records:
        did = str(rec.get('disease_id') or '').strip()
        name = (rec.get('name') or '').strip()
        if did and name:
            name_to_id[name] = disease_node_id(did)

    with open(triples_path, 'w', encoding='utf-8') as f:
        for rec in records:
            did = str(rec.get('disease_id') or '').strip()
            name = (rec.get('name') or '').strip()
            if not did or not name:
                continue
            subj = disease_node_id(did)
            content = rec.get('content') if isinstance(rec.get('content'), dict) else {}

            # literal property triples
            for pred in ['overview','cause','prevent','symptom','inspect','diagnosis','treat','nursing','food']:
                val = content.get(pred)
                if isinstance(val, str) and val.strip():
                    f.write(json.dumps({'subject': subj, 'predicate': pred, 'object': val, 'object_is_literal': True}, ensure_ascii=False) + '\n')

            # 疾病间并发关系（仅当并发症名称能匹配到其他疾病）
            basic_info = content.get('basic_info') if isinstance(content, dict) else None
            if isinstance(basic_info, dict):
                comps = basic_info.get('并发症')
                comp_list: List[str] = []
                if isinstance(comps, list):
                    comp_list = [x for x in comps if isinstance(x, str) and x.strip()]
                elif isinstance(comps, str):
                    comp_list = [x.strip() for x in comps.replace('、', ' ').replace(',', ' ').split() if x.strip()]
                for comp_name in comp_list:
                    target = name_to_id.get(comp_name)
                    if target and target != subj:
                        f.write(json.dumps({'subject': subj, 'predicate': 'COMORBID_WITH', 'object': target, 'object_is_literal': False}, ensure_ascii=False) + '\n')
        


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Convert details_both.json to Neo4j CSV and JSONL triples')
    p.add_argument('--input', default='details_both.json')
    p.add_argument('--nodes', default='neo4j/nodes.csv')
    p.add_argument('--rels', default='neo4j/relations.csv')
    p.add_argument('--triples', default='triples.jsonl')
    return p.parse_args()


def main():
    args = parse_args()
    records = read_json(args.input)
    nodes, edges = build_graph(records)
    write_neo4j_csv(nodes, edges, args.nodes, args.rels)
    write_triples_jsonl(records, args.triples)
    print(f"Nodes: {len(nodes)}, Relations: {len(edges)}")
    print(f"Written: {args.nodes}, {args.rels}, {args.triples}")


if __name__ == '__main__':
    main()


