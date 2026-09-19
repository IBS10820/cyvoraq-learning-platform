import io, os, re, json, html, tempfile
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from PIL import Image as PILImage, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

ROWS = [
  {
    "no": "1",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/44976.jpg",
    "name": "MCR Olba Nitrile Foam Work Gloves - Large",
    "desc": "General handling and grip gloves for everyday work.",
    "qty": "2",
    "price": "£3.58",
    "store": "Toolstation",
    "total": "£7.16",
    "url": "https://www.toolstation.com/mcr-olba-general-purpose-nitrile-foam-gloves/p44976"
  },
  {
    "no": "2",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/75039.jpg",
    "name": "MCR CT1052NF Cut-Resistant Gloves - Large",
    "desc": "Cut-resistant gloves for handling sharp materials.",
    "qty": "1",
    "price": "£9.09",
    "store": "Toolstation",
    "total": "£9.09",
    "url": "https://www.toolstation.com/mcr-ct1052nf-nitrile-foam-cut-resistant-gloves/p75039"
  },
  {
    "no": "3",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/38131.jpg",
    "name": "Blue Powder-Free Nitrile Disposable Gloves - 100 Pack",
    "desc": "Disposable gloves for paint, sealants and dirty jobs.",
    "qty": "1",
    "price": "£13.29",
    "store": "Toolstation",
    "total": "£13.29",
    "url": "https://www.toolstation.com/search?q=38131"
  },
  {
    "no": "4",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/48827.jpg",
    "name": "JSP Stealth Clear Safety Glasses",
    "desc": "Eye protection for drilling, sanding and cutting.",
    "qty": "1",
    "price": "£4.49",
    "store": "Toolstation",
    "total": "£4.49",
    "url": "https://www.toolstation.com/jsp-stealth-safety-glasses-clear/p48827"
  },
  {
    "no": "5",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/80177.jpg",
    "name": "JSP Force8 Half Mask + P3 PressToCheck Filters",
    "desc": "Reusable industrial respirator for dust-producing work.",
    "qty": "1",
    "price": "£28.49",
    "store": "Toolstation",
    "total": "£28.49",
    "url": "https://www.toolstation.com/jsp-force8-mask-with-p3-presstocheck-filters/p80177"
  },
  {
    "no": "6",
    "img": "https://media.screwfix.com/is/image/ae235/401YW_P",
    "name": "Site Premium Ear Defenders 35dB",
    "desc": "Hearing protection for saws, grinders and SDS drilling.",
    "qty": "1",
    "price": "£12.99",
    "store": "Screwfix",
    "total": "£12.99",
    "url": "https://www.screwfix.com/search?search=401YW"
  },
  {
    "no": "7",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/AA214.jpg",
    "name": "Maverick Safety Disposable Hooded Coverall - Large",
    "desc": "Disposable body protection for dusty and paint jobs.",
    "qty": "2",
    "price": "£2.99",
    "store": "Toolstation",
    "total": "£5.98",
    "url": "https://www.toolstation.com/search?q=AA214"
  },
  {
    "no": "8",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/AB195.jpg",
    "name": "Maverick Safety Gel Knee Pads",
    "desc": "Knee protection for decorating, flooring and low-level work.",
    "qty": "1",
    "price": "£14.99",
    "store": "Toolstation",
    "total": "£14.99",
    "url": "https://www.toolstation.com/search?q=AB195"
  },
  {
    "no": "9",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/800/12034.jpg",
    "name": "Stanley Gladiator Waterproof Safety Boots",
    "desc": "Safety footwear for site and property-maintenance work.",
    "qty": "1",
    "price": "£31.98",
    "store": "Toolstation",
    "total": "£31.98",
    "url": "https://www.toolstation.com/stanley-gladiator-waterproof-safety-boots/p12034"
  },
  {
    "no": "10",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/50210.jpg",
    "name": "JSP EVO2 Adjustable Safety Helmet - White",
    "desc": "Head protection where job or site conditions require it.",
    "qty": "1",
    "price": "£7.99",
    "store": "Toolstation",
    "total": "£7.99",
    "url": "https://www.toolstation.com/search?q=50210"
  },
  {
    "no": "11",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/10013.jpg",
    "name": "HSE-Compliant First Aid Kit - Medium",
    "desc": "Site first-aid kit suitable for a small team.",
    "qty": "1",
    "price": "£17.49",
    "store": "Toolstation",
    "total": "£17.49",
    "url": "https://www.toolstation.com/search?q=10013"
  },
  {
    "no": "12",
    "img": "https://media.wickes.co.uk/is/image/wickes/GPID_5000182130_00?$largeNormal$=&defaultImage=wickes%2F2018-Wickes-Missing-Product-650x650",
    "name": "Wickes Painting & Decorating Set - 20 Pieces",
    "desc": "Rollers, mini rollers, brushes, trays and extension pole.",
    "qty": "1",
    "price": "£25.00",
    "store": "Wickes",
    "total": "£25.00",
    "url": "https://www.wickes.co.uk/Wickes-Painting%2BDecorating-Set---20-Pieces/p/322499"
  },
  {
    "no": "13",
    "img": "https://media.wickes.co.uk/is/image/wickes/T3274_607340_00?$largeNormal$=&defaultImage=wickes%2F2018-Wickes-Missing-Product-650x650",
    "name": "Wickes Trade Telescopic Roller Extension Pole 1.4-2.4m",
    "desc": "Longer pole for ceilings and high walls.",
    "qty": "1",
    "price": "£14.50",
    "store": "Wickes",
    "total": "£14.50",
    "url": "https://www.wickes.co.uk/Trade-Telescopic-Roller-Extension-Pole---1-4-to-2-4m/p/607340"
  },
  {
    "no": "14",
    "img": "https://media.diy.com/is/image/Kingfisher/goodhome-large-protector-roll-l-4m-x-w-3m~5059340015248_01c?$MOB_PREV$=&$height=600&$width=600",
    "name": "GoodHome Large Protector Roll 4m x 3m",
    "desc": "Floor and furniture protection while painting.",
    "qty": "2",
    "price": "£4.50",
    "store": "B&Q",
    "total": "£9.00",
    "url": "https://www.diy.com/departments/goodhome-large-protector-roll-l-4m-x-w-3m/5059340015248_BQ.prd"
  },
  {
    "no": "15",
    "img": "https://media.diy.com/is/image/Kingfisher/goodhome-8l-paint-scuttle~5059340016900_02c?$MOB_PREV$=&$height=600&$width=600",
    "name": "GoodHome 8L Paint Scuttle",
    "desc": "Paint bucket/scuttle for roller work.",
    "qty": "1",
    "price": "£7.00",
    "store": "B&Q",
    "total": "£7.00",
    "url": "https://www.diy.com/departments/goodhome-8l-paint-scuttle/5059340016900_BQ.prd"
  },
  {
    "no": "16",
    "img": "https://media.wickes.co.uk/is/image/wickes/T3274_154826_01?$largeNormal$=&defaultImage=wickes%2F2018-Wickes-Missing-Product-650x650",
    "name": "Wickes Multi-Surface Masking Tape 48mm x 50m - Pack 4",
    "desc": "Masking and edge protection for decorating.",
    "qty": "1",
    "price": "£9.00",
    "store": "Wickes",
    "total": "£9.00",
    "url": "https://www.wickes.co.uk/Wickes-Multi-Surface-Cream-Masking-Tape---48mm-x-50m---Pack-of-4/p/154826"
  },
  {
    "no": "17",
    "img": "https://media.wickes.co.uk/is/image/wickes/B0089_600227_00?$largeNormal$=&defaultImage=wickes%2F2018-Wickes-Missing-Product-650x650",
    "name": "Wickes All-Purpose Ready Mixed Filler - 1kg",
    "desc": "Filling holes and minor wall defects before painting.",
    "qty": "1",
    "price": "£5.75",
    "store": "Wickes",
    "total": "£5.75",
    "url": "https://www.wickes.co.uk/Wickes-All-Purpose-Ready-Mixed-Filler---1kg/p/600227"
  },
  {
    "no": "18",
    "img": "https://media.wickes.co.uk/image/upload/b_rgb:FFFFFF,c_pad,dpr_1.0,f_jpg,h_500,q_auto:good,w_500/c_pad,h_500,w_500/v1/products/wickes/GPID_1100629264_00?pgw=1",
    "name": "Wickes White Decorators Caulk 300ml",
    "desc": "Flexible gap filling around frames, skirting and trim.",
    "qty": "3",
    "price": "£1.50",
    "store": "Wickes",
    "total": "£4.50",
    "url": "https://www.wickes.co.uk/Wickes-White-Decorators-Caulk---300ml/p/215370"
  },
  {
    "no": "19",
    "img": "https://media.wickes.co.uk/is/image/wickes/GPID_1100629311_00?$largeNormal$=&defaultImage=wickes%2F2018-Wickes-Missing-Product-650x650",
    "name": "Wickes White All-Purpose Silicone Sealant 300ml",
    "desc": "Sealing wet areas and general maintenance joints.",
    "qty": "2",
    "price": "£5.10",
    "store": "Wickes",
    "total": "£10.20",
    "url": "https://www.wickes.co.uk/Wickes-White-All-Purpose-Silicone-Sealant---300ml/p/215357"
  },
  {
    "no": "20",
    "img": "https://www.dema.be/60267-thickbox_default/wolfcraft-pistolet-a-silicone-mg100.jpg",
    "name": "Wolfcraft MG100 Caulking Gun",
    "desc": "Applicator for caulk, silicone and cartridge adhesives.",
    "qty": "1",
    "price": "£8.00",
    "store": "Wickes",
    "total": "£8.00",
    "url": "https://www.wickes.co.uk/Wolfcraft-MG-100-Caulking-Gun/p/489918"
  },
  {
    "no": "21",
    "img": "https://media.diy.com/is/image/Kingfisher/magnusson-122-piece-black-orange-hand-tool-kit-uotk122~5063022542922_07c?$MOB_PREV$=&$height=1200&$width=1200",
    "name": "Magnusson Hand Tool Kit - 122 Pieces",
    "desc": "Main hand-tool kit: sockets, screwdrivers, pliers, hammer, hex keys and more.",
    "qty": "1",
    "price": "£149.99",
    "store": "Screwfix",
    "total": "£149.99",
    "url": "https://www.screwfix.com/search?search=910AG"
  },
  {
    "no": "22",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/85458.jpg",
    "name": "Minotaur Second-Fix Handsaw 500mm",
    "desc": "General timber and board cutting by hand.",
    "qty": "1",
    "price": "£5.99",
    "store": "Toolstation",
    "total": "£5.99",
    "url": "https://www.toolstation.com/minotaur-second-fix-handsaw/p85458"
  },
  {
    "no": "23",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/82899.jpg",
    "name": "Roughneck Toolbox Bar Set - 4 Piece",
    "desc": "Pry bars for removal, demolition and fitting jobs.",
    "qty": "1",
    "price": "£18.39",
    "store": "Toolstation",
    "total": "£18.39",
    "url": "https://www.toolstation.com/search?q=82899"
  },
  {
    "no": "24",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/21564.jpg",
    "name": "Irwin Quick-Grip Mini Clamps 300mm - 2 Pack",
    "desc": "Holding timber and components while cutting, drilling or gluing.",
    "qty": "1",
    "price": "£10.99",
    "store": "Toolstation",
    "total": "£10.99",
    "url": "https://www.toolstation.com/search?q=21564"
  },
  {
    "no": "25",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/98183.jpg",
    "name": "Minotaur Tilt & Fold Workbench",
    "desc": "Portable work support for cutting and assembly.",
    "qty": "1",
    "price": "£29.99",
    "store": "Toolstation",
    "total": "£29.99",
    "url": "https://www.toolstation.com/minotaur-tilt-fold-workbench/p98183"
  },
  {
    "no": "26",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/69682.jpg",
    "name": "Minotaur Trade Spirit Level 1200mm",
    "desc": "Level and plumb checks for fitting and handyman work.",
    "qty": "1",
    "price": "£22.99",
    "store": "Toolstation",
    "total": "£22.99",
    "url": "https://www.toolstation.com/search?q=69682"
  },
  {
    "no": "27",
    "img": "https://media.screwfix.com/is/image/ae235/748AK_P",
    "name": "Erbauer 18V Brushless Cordless 6-Piece Kit + 3x4Ah Batteries",
    "desc": "Combi drill, impact driver, SDS+, circular saw, jigsaw, multi-tool, batteries, charger and bag.",
    "qty": "1",
    "price": "£479.99",
    "store": "Screwfix",
    "total": "£479.99",
    "url": "https://www.screwfix.com/p/erbauer-18v-3-x-4-0ah-li-ion-ext-brushless-cordless-6-piece-kit/748ak"
  },
  {
    "no": "28",
    "img": "https://www.ikmal.com.tr/idea/ol/37/myassets/products/324/3b84033d-ee1e-4b13-8a9b-f3493c9f4588.jpeg?revision=1777982241",
    "name": "DEWALT Multi-Material Drill & Screwdriver Bit Set - 100 Pieces",
    "desc": "Bits for wood, metal, plastic and masonry plus screwdriver bits.",
    "qty": "1",
    "price": "£19.99",
    "store": "Screwfix",
    "total": "£19.99",
    "url": "https://www.screwfix.com/p/dewalt-multi-material-drill-bit-set-100-pieces/13266"
  },
  {
    "no": "29",
    "img": "https://media.screwfix.com/is/image/ae235/709YM_P",
    "name": "Erbauer 18V Brushless Angle Grinder 115mm - Bare",
    "desc": "Grinding and cutting with the correct disc and guard.",
    "qty": "1",
    "price": "£69.99",
    "store": "Screwfix",
    "total": "£69.99",
    "url": "https://www.screwfix.com/p/erbauer-eri1082grd-18v-li-ion-ext-4-5-brushless-cordless-angle-grinder-bare/709ym"
  },
  {
    "no": "30",
    "img": "https://media.screwfix.com/is/image/ae235/102YM_P",
    "name": "Erbauer 18V Brushless Reciprocating Saw - Bare",
    "desc": "Fast rough cutting and demolition with the correct blade.",
    "qty": "1",
    "price": "£69.99",
    "store": "Screwfix",
    "total": "£69.99",
    "url": "https://www.screwfix.com/p/erbauer-eri1090rsp-18v-li-ion-ext-brushless-cordless-reciprocating-saw-bare/102ym"
  },
  {
    "no": "31",
    "img": "https://media.screwfix.com/is/image/ae235/919EH_P",
    "name": "Titan 125mm Random Orbit Sander",
    "desc": "Powered sanding for preparation and finishing.",
    "qty": "1",
    "price": "£29.97",
    "store": "Screwfix",
    "total": "£29.97",
    "url": "https://www.screwfix.com/p/titan-ttb1327sdr-125mm-electric-random-orbit-sander-220-240v/919eh"
  },
  {
    "no": "32",
    "img": "https://media.screwfix.com/is/image/ae235/912KJ_P",
    "name": "Titan 2000W Heat Gun",
    "desc": "Paint stripping, heat-shrink and controlled heating tasks.",
    "qty": "1",
    "price": "£19.97",
    "store": "Screwfix",
    "total": "£19.97",
    "url": "https://www.screwfix.com/p/titan-ttb773htg-2000w-electric-heat-gun-220-240v/912KJ"
  },
  {
    "no": "33",
    "img": "https://cdn.idealo.com/folder/Product/200989/0/200989073/s1_produktbild_max_10/wagner-steamforce-dampftapetenabloeser-2000w-0339050.jpg",
    "name": "Wagner SteamForce 2000W Wallpaper Stripper",
    "desc": "Steam wallpaper removal.",
    "qty": "1",
    "price": "£39.99",
    "store": "Screwfix",
    "total": "£39.99",
    "url": "https://www.screwfix.com/search?search=567KR"
  },
  {
    "no": "34",
    "img": "https://media.screwfix.com/is/image/ae235/150RG_A2",
    "name": "Titan 20L M-Class Wet & Dry Dust Extractor",
    "desc": "Industrial dust extraction/vacuum for sanding and cutting work.",
    "qty": "1",
    "price": "£119.99",
    "store": "Screwfix",
    "total": "£119.99",
    "url": "https://www.screwfix.com/p/titan-ttb922vac-m-1400w-20ltr-m-class-wet-dry-vacuum-220-240v/150rg"
  },
  {
    "no": "35",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/80523.jpg",
    "name": "Stanley Rechargeable Folding Work Light",
    "desc": "Portable task lighting for interiors and site work.",
    "qty": "1",
    "price": "£47.29",
    "store": "Toolstation",
    "total": "£47.29",
    "url": "https://www.toolstation.com/search?q=80523"
  },
  {
    "no": "36",
    "img": "https://www.robertdyas.co.uk/media/catalog/product/2/4/248883.jpg?bg-color=255%2C255%2C255&canvas=1200%3A1200&height=1200&quality=80&width=1200",
    "name": "PRO XT 25m 4-Gang Open Cable Reel",
    "desc": "Long extension reel for powered tools on site.",
    "qty": "1",
    "price": "£29.99",
    "store": "Online / Trade",
    "total": "£29.99",
    "url": "https://www.chadwicks.ie/25m-pro-xt-4gang-open-reel-cable-reel-35066.html"
  },
  {
    "no": "37",
    "img": "https://media.diy.com/is/image/Kingfisher/masterplug-13a-rcd-adaptor-plug-plug-through~5015056379500_06c_bq?$MOB_PREV$=&$height=600&$width=600",
    "name": "Masterplug 13A Plug-Through Active RCD Adaptor",
    "desc": "Extra shock protection for portable mains tools.",
    "qty": "1",
    "price": "£10.99",
    "store": "Screwfix",
    "total": "£10.99",
    "url": "https://www.screwfix.com/p/masterplug-13a-unfused-plug-through-active-rcd-adaptor/63731"
  },
  {
    "no": "38",
    "img": "https://a.allegroimg.com/original/11aa22/92da274444338d7fa718e95a22af/DEWALT-DALMIERZ-LASEROWY-USB-16m-DW055PL-14183269097",
    "name": "DEWALT DW055PL Laser Distance Measure 16m",
    "desc": "Fast room and site measurements for quoting and layout.",
    "qty": "1",
    "price": "£26.99",
    "store": "Toolstation",
    "total": "£26.99",
    "url": "https://www.toolstation.com/search?q=DW055PL"
  },
  {
    "no": "39",
    "img": "https://www.hancocks-building-supplies.co.uk/media/catalog/product/cache/006fe97f8385e32c54aff4bd1e3d81cb/p/r/product_image_-_2025-08-14t101840.444.png",
    "name": "Stanley S160 Stud Detector",
    "desc": "Locates studs and hidden structures before drilling or fixing.",
    "qty": "1",
    "price": "£29.99",
    "store": "Toolstation",
    "total": "£29.99",
    "url": "https://www.toolstation.com/search?q=62975"
  },
  {
    "no": "40",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/388/55818.jpg",
    "name": "Draper Mini Moisture Meter",
    "desc": "Checks moisture before painting or repair work.",
    "qty": "1",
    "price": "£19.99",
    "store": "Toolstation",
    "total": "£19.99",
    "url": "https://www.toolstation.com/draper-mini-moisture-meter/p55818"
  },
  {
    "no": "41",
    "img": "https://a.allegroimg.com/original/11a1d2/bf5a6bce48f697e679c0989178b8/STANLEY-LASER-KRZYZOWY-POZIOMICA-CUBIX-77340-QUICK-FATMAX-STHT77498-1",
    "name": "Stanley Cubix Red Laser Level",
    "desc": "Cross-line levelling for shelves, pictures, fittings and layouts.",
    "qty": "1",
    "price": "£47.99",
    "store": "Toolstation",
    "total": "£47.99",
    "url": "https://www.toolstation.com/search?q=18629"
  },
  {
    "no": "42",
    "img": "https://cdn.aws.toolstation.com/images/141020-UK/800/30254-4.jpg",
    "name": "Werner High Handrail Step Ladder - 6 Tread",
    "desc": "Access for normal interior painting and handyman work.",
    "qty": "1",
    "price": "£62.98",
    "store": "Toolstation",
    "total": "£62.98",
    "url": "https://www.toolstation.com/werner-high-handrail-step-ladder/p30254"
  },
  {
    "no": "43",
    "img": "https://www.workplace-products.co.uk/pub/media/catalog/product/o/d/odd-job_1.jpg",
    "name": "Werner Odd Job Work Platform",
    "desc": "Low-level work platform for decorating and repairs.",
    "qty": "1",
    "price": "£39.99",
    "store": "Toolstation",
    "total": "£39.99",
    "url": "https://www.toolstation.com/werner-odd-job-platform/p74592"
  },
  {
    "no": "44",
    "img": "https://www.laddersukdirect.co.uk/images/product-zoom/b0eef989-d44a-4e4f-9be6-fad422b80dcf/werner-combination-ladder-5-in-1-with-platform.jpg",
    "name": "Werner 5-in-1 Combination Ladder with Platform",
    "desc": "Flexible higher-access ladder system.",
    "qty": "1",
    "price": "£129.98",
    "store": "Toolstation",
    "total": "£129.98",
    "url": "https://www.toolstation.com/werner-5-in-1-combination-ladder/p65318"
  },
  {
    "no": "45",
    "img": "https://media.screwfix.com/is/image/ae235/541EH_P",
    "name": "Titan 210mm Sliding Mitre Saw",
    "desc": "Accurate repeat cuts for skirting, architrave, trim and timber.",
    "qty": "1",
    "price": "£99.99",
    "store": "Screwfix",
    "total": "£99.99",
    "url": "https://www.screwfix.com/p/titan-ttb1363msw-210mm-electric-single-bevel-sliding-mitre-saw-220-240v/541eh"
  },
  {
    "no": "46",
    "img": "https://media.screwfix.com/is/image/ae235/360AE_P",
    "name": "Titan 145bar Electric Pressure Washer",
    "desc": "Exterior and property cleaning/preparation.",
    "qty": "1",
    "price": "£99.99",
    "store": "Screwfix",
    "total": "£99.99",
    "url": "https://www.screwfix.com/p/titan-ttb1222prw-145bar-electric-high-pressure-washer-1800w-220-240v/360ae"
  }
]
OUT = Path("zenfixandfinish/Zen_Fix_Finish_Simple_Tool_Shopping_List_2026_WITH_PRODUCT_IMAGES.pdf")
IMGDIR = Path("zenfixandfinish/_product_images")
IMGDIR.mkdir(parents=True, exist_ok=True)

S = requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36","Accept":"image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"})

def save_image_bytes(content, path):
    im=PILImage.open(io.BytesIO(content))
    if im.mode not in ("RGB","RGBA"): im=im.convert("RGB")
    if im.mode=="RGBA":
        bg=PILImage.new("RGB", im.size, "white"); bg.paste(im, mask=im.getchannel("A")); im=bg
    else: im=im.convert("RGB")
    im.thumbnail((700,700), PILImage.Resampling.LANCZOS)
    canvas=PILImage.new("RGB",(700,700),"white")
    x=(700-im.width)//2; y=(700-im.height)//2
    canvas.paste(im,(x,y))
    canvas.save(path,"JPEG",quality=90,optimize=True)

def fetch_image(row, idx):
    dst=IMGDIR/f"{idx:02d}.jpg"
    candidates=[row["img"]]
    # Also try common Screwfix size suffix where supplied image URL is image-server based
    if "media.screwfix.com/is/image/" in row["img"] and "?" not in row["img"]:
        candidates += [row["img"]+"?$fxSharpen$=&dpr=on&hei=700&wid=700", row["img"]+"_A3"]
    for u in candidates:
        try:
            r=S.get(u,timeout=30,allow_redirects=True)
            if r.ok and len(r.content)>2000:
                save_image_bytes(r.content,dst); return dst, u
        except Exception:
            pass
    # Fallback: scrape product page for og:image/twitter:image and first likely product image
    try:
        rp=S.get(row["url"],timeout=30,allow_redirects=True)
        if rp.ok:
            soup=BeautifulSoup(rp.text,"html.parser")
            urls=[]
            for key,val in [("property","og:image"),("name","twitter:image"),("property","twitter:image")]:
                tag=soup.find("meta",attrs={key:val})
                if tag and tag.get("content"): urls.append(tag["content"])
            for tag in soup.find_all("img"):
                src=tag.get("src") or tag.get("data-src") or tag.get("data-lazy-src")
                alt=(tag.get("alt") or "").lower()
                if src and (row["name"].split()[0].lower() in alt or "product" in alt):
                    urls.append(src)
            for u in urls:
                if u.startswith("//"): u="https:"+u
                if u.startswith("/"):
                    from urllib.parse import urljoin
                    u=urljoin(row["url"],u)
                try:
                    r=S.get(u,timeout=30,allow_redirects=True)
                    if r.ok and len(r.content)>2000:
                        save_image_bytes(r.content,dst); return dst, u
                except Exception:
                    pass
    except Exception:
        pass
    return None, None

fetched=[]
for i,row in enumerate(ROWS,1):
    path,used=fetch_image(row,i)
    fetched.append(path)
    print(f"{i:02d} {'OK' if path else 'FAIL'} {row['name']} {used or ''}")

styles=getSampleStyleSheet()
title=ParagraphStyle("title",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=18,leading=20,textColor=colors.HexColor("#172026"))
sub=ParagraphStyle("sub",parent=styles["Normal"],fontSize=8,leading=10,textColor=colors.HexColor("#667078"))
hdr=ParagraphStyle("hdr",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=7,leading=8,textColor=colors.white,alignment=TA_CENTER)
item=ParagraphStyle("item",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=7.4,leading=8.5,textColor=colors.HexColor("#172026"))
desc=ParagraphStyle("desc",parent=styles["Normal"],fontSize=6.2,leading=7.4,textColor=colors.HexColor("#687078"))
cell=ParagraphStyle("cell",parent=styles["Normal"],fontSize=7,leading=8,textColor=colors.HexColor("#172026"),alignment=TA_CENTER)
price=ParagraphStyle("price",parent=cell,fontName="Helvetica-Bold",alignment=TA_RIGHT)

page_w,page_h=landscape(A4)
doc=SimpleDocTemplate(str(OUT),pagesize=landscape(A4),rightMargin=7*mm,leftMargin=7*mm,topMargin=8*mm,bottomMargin=9*mm)

story=[
    Paragraph("ZEN FIX & FINISH - Tool Shopping List with Actual Product Images",title),
    Paragraph("Painting + handyman starter setup | UK prices checked 19 September 2026 | 46 line items | Estimated total: <b>£1,981.27</b>",sub),
    Spacer(1,3*mm)
]
data=[[Paragraph("No.",hdr),Paragraph("Actual product image",hdr),Paragraph("Item name & description",hdr),Paragraph("Qty",hdr),Paragraph("Price each",hdr),Paragraph("Store",hdr),Paragraph("Line total",hdr)]]
for i,(row,imgpath) in enumerate(zip(ROWS,fetched),1):
    if imgpath:
        im=Image(str(imgpath),width=24*mm,height=24*mm)
        im.hAlign="CENTER"
        im._restrictSize(24*mm,24*mm)
        pic=im
    else:
        pic=Paragraph("<b>Image unavailable</b><br/><font size='5'>See retailer link in item name</font>",desc)
    name=html.escape(row["name"])
    d=html.escape(row["desc"])
    linked=f'<link href="{html.escape(row["url"])}" color="#172026"><b>{name}</b></link><br/><font size="6.1" color="#687078">{d}</font>'
    data.append([
        Paragraph(str(i),cell), pic, Paragraph(linked,item), Paragraph(row["qty"],cell),
        Paragraph(row["price"],price), Paragraph(html.escape(row["store"]),cell), Paragraph(row["total"],price)
    ])
data.append(["","",Paragraph("<b>ESTIMATED TOTAL</b>",item),"","","",Paragraph("<b>£1,981.27</b>",price)])

tbl=Table(data,colWidths=[10*mm,30*mm,111*mm,13*mm,23*mm,27*mm,24*mm],repeatRows=1,hAlign="LEFT")
tbl.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#202A30")),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("GRID",(0,0),(-1,-2),0.35,colors.HexColor("#D9DDE0")),
    ("ROWBACKGROUNDS",(0,1),(-1,-2),[colors.white,colors.HexColor("#FAFBFB")]),
    ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#11191E")),
    ("TEXTCOLOR",(0,-1),(-1,-1),colors.white),
    ("SPAN",(2,-1),(5,-1)),
    ("ALIGN",(0,1),(0,-1),"CENTER"),
    ("ALIGN",(1,1),(1,-2),"CENTER"),
    ("ALIGN",(3,1),(3,-1),"CENTER"),
    ("ALIGN",(4,1),(4,-1),"RIGHT"),
    ("ALIGN",(6,1),(6,-1),"RIGHT"),
    ("LEFTPADDING",(0,0),(-1,-1),3),
    ("RIGHTPADDING",(0,0),(-1,-1),3),
    ("TOPPADDING",(0,1),(-1,-2),3),
    ("BOTTOMPADDING",(0,1),(-1,-2),3),
]))
story.append(tbl)
story.append(Spacer(1,3*mm))
story.append(Paragraph("The image column contains retailer/manufacturer product photographs downloaded from the listed product sources. Product names are clickable. Prices can change; re-check the retailer immediately before purchase.",sub))

def footer(canvas,doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#C69232")); canvas.setLineWidth(.6)
    canvas.line(7*mm,6.5*mm,page_w-7*mm,6.5*mm)
    canvas.setFont("Helvetica",6); canvas.setFillColor(colors.HexColor("#707980"))
    canvas.drawString(7*mm,3.2*mm,"Zen Fix & Finish Property Services - 2026 startup shopping list")
    canvas.drawRightString(page_w-7*mm,3.2*mm,f"Page {doc.page}")
    canvas.restoreState()

doc.build(story,onFirstPage=footer,onLaterPages=footer)

failed=[ROWS[i]["name"] for i,p in enumerate(fetched) if not p]
Path("zenfixandfinish/image-fetch-report.txt").write_text("\n".join(["FAILED IMAGES:"]+failed),encoding="utf-8")
print("PDF",OUT)
print("FAILED",len(failed))

# build trigger
