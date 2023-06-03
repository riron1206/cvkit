import argparse
import os
from glob import glob
import pandas as pd
import numpy as np
from loguru import logger
from pathlib import Path
from pprint import pprint, pformat
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold

from src.utils import get_audio_info

CLASSES = ["abethr1", "abhori1", "abythr1", "afbfly1", "afdfly1", "afecuc1", "affeag1", "afghor1", "afmdov1", "afpfly1",
"afpwag1", "afrgos1", "afrgrp1", "afrjac1", "afrthr1", "amesun2", "augbuz1", "bagwea1", "barswa", "bawhor2",
"bcbeat1", "beasun2", "bkctch1", "bkfruw1", "blacra1", "blacuc1", "blakit1", "blaplo1", "blbpuf2", "blcapa2",
"blfbus1", "blhgon1", "blhher1", "blksaw1", "blnmou1", "blnwea1", "bltapa1", "bltori1", "blwlap1", "brcale1",
"brctch1", "brican1", "brobab1", "broman1", "brosun1", "brubru1", "brwwar1", "bswdov1", "btweye2", "bubwar2",
"butapa1", "cabgre1", "carcha1", "carwoo1", "categr", "ccbeat1", "chewea1", "chibat1", "chtapa3", "chucis1",
"cibwar1", "cohmar1", "colsun2", "combul2", "combuz1", "comsan", "crheag1", "crohor1", "darbar1", "didcuc1",
"easmog1", "eaywag1", "edcsun3", "egygoo", "eswdov1", "eubeat1", "fatrav1", "fislov1", "fotdro5", "gabgos2",
"gargan", "gbesta1", "gnbcam2", "gnhsun1", "gobbun1", "grbcam1", "grccra1", "grecor", "greegr", "grewoo2",
"grwpyt1", "gryapa1", "grywrw1", "gybfis1", "gycwar3", "gyhbus1", "gyhkin1", "gyhneg1", "gyhspa1", "hadibi1",
"hamerk1", "hartur1", "helgui", "hoopoe", "huncis1", "kerspa2", "klacuc1", "kvbsun1", "laudov1", "lawgol",
"lesmaw1", "lessts1", "libeat1", "litegr", "litswi1", "litwea1", "loceag1", "luebus1", "mabeat1", "malkin1",
"marsun2", "meypar1", "moccha1", "mouwag1", "ndcsun2", "nobfly1", "norbro1", "norcro1", "norfis1", "norpuf1",
"nubwoo1", "pabspa1", "palfly2", "piecro1", "piekin1", "pitwhy", "purgre2", "pygbat1", "quailf1", "ratcis1",
"raybar1", "rbsrob1", "rebfir2", "rebhor1", "reboxp1", "reccor", "reccuc1", "reedov1", "refbar2", "refcro1",
"reftin1", "reisee2", "rerswa1", "rewsta1", "rindov", "rocmar2", "rostur1", "ruegls1", "sccsun2", "scrcha1",
"scthon1", "sichor1", "sincis1", "slbgre1", "slcbou1", "sltnig1", "sobfly1", "somgre1", "somtit4", "soucit1",
"soufis1", "spemou2", "spepig1", "spewea1", "spfbar1", "spfwea1", "spmthr1", "spwlap1", "squher1", "strher",
"strsee1", "subbus1", "supsta1", "tafpri1", "tamdov1", "thrnig1", "trobou1", "varsun2", "vibsta2", "vilwea1",
"vimwea1", "walsta1", "wbgbir1", "wbrcha2", "wbswea1", "wfbeat1", "whbcan1", "whbcou1", "whbtit5", "whbwea1",
"whbwhe3", "wheslf1", "whihel1", "whrshr1", "wlwwar", "wookin1", "woosan", "wtbeat1", "yebapa1", "yebbar1",
"yebduc1", "yebere1", "yebgre1", "yeccan1", "yefcan", "yelbis1", "yenspu1", "yertin1", "yesbar1", "yespet1",
"yetgre1", "yewgre1", "afgfly1", "afpkin1", "bawman1", "bltbar1", "brcsta1", "brcwea1", "brrwhe3", "brtcha1",
"chespa1", "crefra2", "darter3", "dotbar1", "dutdov1", "equaka1", "fatwid1", "gobsta5", "gobwea1", "golher1",
"gytbar1", "hipbab1", "hunsun2", "joygre1", "lotcor1", "lotlap1", "macshr1", "marsto1", "mcptit1", "palpri1",
"refwar2", "rehblu1", "rehwea1", "rufcha2", "sacibi2", "shesta1", "stusta1", "tacsun1", "whbcro2", "whcpri2",
"whctur2", "whhsaw1", "witswa1", "yebsto1"]

def main(args):
    logger.info('\nargs:\n'+pformat(vars(args)))

    data_dir = Path(args.data_dir)
    df = pd.read_csv(data_dir / 'train_metadata.csv')
    df['path'] = data_dir / 'train_audio'
    df['path'] = df['path'] / (df['filename'])
    df['class_id'] = df['primary_label'].map(dict(zip(CLASSES, list(range(len(CLASSES))))))
    df['class'] = df['primary_label']

    logger.info('CV split')
    kf = StratifiedKFold(n_splits=args.num_fold, shuffle=True, random_state=args.seed)
    for fold, (train_index, val_index) in enumerate(kf.split(df.values, df['class_id'])):
        df.loc[val_index, "fold"] = int(fold)
    df["fold"] = df["fold"].astype(int)

    # 音声データのメタ情報の列も入れる
    info_dict_list = [get_audio_info(p) for p in df['path'].values]
    df_info = pd.DataFrame(info_dict_list)
    df = df.join(df_info)

    logger.info('Save')
    df = df[['path', 'class_id', 'class', 'fold', 'frames', 'sr', 'duration']]
    df.to_csv(args.output_path, index=False)

    logger.info('\n'+pformat(df))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', type=str)
    parser.add_argument('output_path', type=str)
    parser.add_argument('--seed', type=int, default=2021)
    parser.add_argument('--num_fold', type=int, default=5)
    args = parser.parse_args()
    main(args)