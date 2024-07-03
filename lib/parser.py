
from classes.Entry import Entry
from datetime import datetime
from icecream import ic
from lxml import etree
from pathlib import Path


def parse_file(input_file: Path, default_timezone = datetime.now().tzinfo) -> tuple[list[Entry], float, float, float]:

    tree = etree.parse(input_file)
    root = tree.getroot()

    namespaces = { a: b for a, b in root.nsmap.items() if a is not None }
    ic(namespaces)

    def fullName(ns, name, namespaces=namespaces):
        return f"{{{namespaces[ns]}}}{name}"

    nodeEnvelope = root.find("ns4:CBIEnvelBkToCstmrStmtReqLogMsg", namespaces )

    assert(nodeEnvelope is not None)

    nodeReqLogMsg = nodeEnvelope.find("ns4:CBIBkToCstmrStmtReqLogMsg", namespaces)

    assert(nodeReqLogMsg is not None)

    nodeDailyReqLogMsg = nodeReqLogMsg.find("ns6:CBIDlyStmtReqLogMsg", namespaces)

    assert(nodeDailyReqLogMsg is not None)

    nodeGroupHeader = None

    entries: list[Entry] = []

    for data in nodeDailyReqLogMsg.iter():
        # ic(data.tag)
        if data.tag == fullName("ns5", "GrpHdr"):
            assert(nodeGroupHeader is None)
            nodeGroupHeader = data

        elif data.tag == fullName("ns5", "Stmt"):
            # electrId = data.attrib['ns5:ElctrncSeqNb']
            # ic(data)

            for inner_data in data.iter():

                if inner_data.tag == fullName("ns5", "Ntry"):
                    entries.append(
                        Entry(namespaces, data, inner_data, "ns5", default_timezone=default_timezone)
                    )

    sorted_entries = sorted(entries, key=lambda x: x.data_valuta.timestamp())


    totale_entrate = sum([x.value for x in sorted_entries if x.sign == "+"])
    totale_uscite = -sum([x.value for x in sorted_entries if x.sign == "-"])

    totale = totale_entrate + totale_uscite

    return sorted_entries, totale_entrate, totale_uscite, totale


