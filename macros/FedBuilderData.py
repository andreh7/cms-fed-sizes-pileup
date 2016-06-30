#!/usr/bin/env python

# FBSet /fb_all_withuTCA_with_CTPPS_TOT
# from hardware database retrieved 2016-05-31
fedBuilderGroups = [
    { "name": "TCDS", "feds": [ 1024 ] },

    { "name": "BPIX3", "feds": [ 16, 17, 18, 19, 20, 21, 22, 23 ] },

    { "name": "BPIX4", "feds": [ 24, 25, 26, 27, 28, 29, 30, 31 ] },

    { "name": "BPIX1", "feds": [ 0, 1, 2, 3, 4, 5, 6, 7 ] },

    { "name": "BPIX2", "feds": [ 8, 9, 10, 11, 12, 13, 14, 15 ] },

    { "name": "CSC+", "feds": [ 831, 832, 833, 834, 835, 836, 837, 838, 839, 841, 842, 843, 844, 845, 846, 847, 848, 849 ] },

    { "name": "CSC-", "feds": [ 851, 852, 853, 854, 855, 856, 857, 858, 859, 861, 862, 863, 864, 865, 866, 867, 868, 869 ] },

    { "name": "CSCTF", "feds": [ 760 ] },

    { "name": "DT", "feds": [ 770, 771, 772, 773, 774 ] },

    { "name": "EB+1", "feds": [ 628, 629, 630, 631, 632, 633, 634, 635, 636 ] },

    { "name": "EB+2", "feds": [ 637, 638, 639, 640, 641, 642, 643, 644, 645 ] },

    { "name": "EB-1", "feds": [ 610, 611, 612, 613, 614, 615, 616, 617, 618 ] },

    { "name": "EB-2", "feds": [ 619, 620, 621, 622, 623, 624, 625, 626, 627 ] },

    { "name": "EE+", "feds": [ 646, 647, 648, 649, 650, 651, 652, 653, 654 ] },

    { "name": "EE-", "feds": [ 601, 602, 603, 604, 605, 606, 607, 608, 609 ] },

    { "name": "ES+1a", "feds": [ 549, 551, 555, 556, 557, 563, 570, 571 ] },

    { "name": "ES+1b", "feds": [ 548, 553, 554, 560, 561, 564, 565, 566, 568, 572, 573, 574 ] },

    { "name": "ES-1a", "feds": [ 524, 525, 531, 532, 537, 539, 545, 546, 547 ] },

    { "name": "ES-1b", "feds": [ 520, 522, 523, 528, 529, 530, 534, 535, 540, 541, 542 ] },

    { "name": "FPIXPixelPilot", "feds": [ 32, 33, 34, 35, 36, 37, 38, 39, 40 ] },

    { "name": "HBHEa", "feds": [ 700, 701, 702, 703, 704, 705 ] },

    { "name": "HBHEauTCA", "feds": [ 1100, 1102, 1104 ] },

    { "name": "HBHEb", "feds": [ 706, 707, 708, 709, 710, 711 ] },

    { "name": "HBHEbuTCA", "feds": [ 1106, 1108, 1110 ] },

    { "name": "HBHEc", "feds": [ 712, 713, 714, 715, 716, 717 ] },

    { "name": "HBHEcuTCA", "feds": [ 1112, 1114, 1116 ] },

    { "name": "HF", "feds": [ 1118, 1120, 1122, 1132 ] },

    { "name": "HOSCAL", "feds": [ 724, 725, 726, 727, 728, 729, 730, 731, 735 ] },

    { "name": "EMTFOMTF", "feds": [ 1380, 1381, 1384, 1385 ] },

    { "name": "BMTFGMTGT", "feds": [ 1376, 1377, 1402, 1404 ] },

    { "name": "CALTRIGUP", "feds": [ 1354, 1356, 1358, 1360 ] },

    { "name": "RPC", "feds": [ 790, 791, 792 ] },

    { "name": "TEC+3a", "feds": [ 268, 269, 270, 271, 272, 273, 274, 275, 300, 301, 302, 303, 304, 305, 306, 307 ] },

    { "name": "TEC+3b", "feds": [ 276, 277, 278, 279, 280, 281, 282, 283, 308, 309, 310, 311, 312, 313, 314, 315 ] },

    { "name": "TEC+1a", "feds": [ 326, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355 ] },

    { "name": "TEC+1b", "feds": [ 316, 317, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340 ] },

    { "name": "TEC+2a", "feds": [ 284, 285, 286, 287, 288, 289, 290, 291, 318, 319, 320, 321, 322, 323, 324, 325 ] },

    { "name": "TEC+2b", "feds": [ 260, 261, 262, 263, 264, 265, 266, 267, 292, 293, 294, 295, 296, 297, 298, 299 ] },

    { "name": "TEC-3a", "feds": [ 220, 221, 222, 223, 224, 225, 226, 227, 244, 245, 246, 247, 248, 249, 250, 251 ] },

    { "name": "TEC-3b", "feds": [ 228, 229, 230, 231, 232, 233, 234, 235, 252, 253, 254, 255, 256, 257, 258, 259 ] },

    { "name": "TEC-1a", "feds": [ 174, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203 ] },

    { "name": "TEC-1b", "feds": [ 164, 165, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188 ] },

    { "name": "TEC-2a", "feds": [ 166, 167, 168, 169, 170, 171, 172, 173, 204, 205, 206, 207, 208, 209, 210, 211 ] },

    { "name": "TEC-2b", "feds": [ 212, 213, 214, 215, 216, 217, 218, 219, 236, 237, 238, 239, 240, 241, 242, 243 ] },

    { "name": "TIBTID4", "feds": [ 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163 ] },

    { "name": "TIBTID5", "feds": [ 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148 ] },

    { "name": "TIBTID6a", "feds": [ 74, 75, 76, 77, 78, 79, 80, 81, 118, 119, 120, 121, 122, 123, 124, 125 ] },

    { "name": "TIBTID6b", "feds": [ 82, 83, 84, 85, 126, 127, 128, 129, 130, 131, 132, 133 ] },

    { "name": "TIBTID1a", "feds": [ 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101 ] },

    { "name": "TIBTID1b", "feds": [ 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117 ] },

    { "name": "TIBTID2", "feds": [ 50, 51, 52, 53, 54, 55, 56, 57, 58, 60, 61 ] },

    { "name": "TIBTID3", "feds": [ 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73 ] },

    { "name": "TOB-1a", "feds": [ 416, 417, 418, 419, 420, 421, 422, 423, 474, 475, 476, 477, 478, 479, 480, 481 ] },

    { "name": "TOB-1b", "feds": [ 402, 403, 404, 405, 406, 424, 425, 426, 482, 483, 484, 485, 486, 487, 488, 489 ] },

    { "name": "TOB-2a", "feds": [ 356, 357, 358, 359, 360, 361, 362, 444, 445, 446, 447, 448, 449, 450 ] },

    { "name": "TOB-2b", "feds": [ 363, 364, 365, 366, 367, 371, 372, 451, 452, 453, 454, 455, 456, 457 ] },

    { "name": "TOB-3a", "feds": [ 386, 387, 388, 389, 390, 391, 392, 393, 430, 431, 432, 433, 434, 435, 436, 437 ] },

    { "name": "TOB-3b", "feds": [ 394, 395, 396, 397, 398, 399, 400, 401, 438, 439, 440, 441, 442, 443 ] },

    { "name": "TOB-4a", "feds": [ 376, 377, 407, 408, 409, 410, 411, 412, 458, 459, 460, 461, 462, 463, 464, 465 ] },

    { "name": "TOB-4b", "feds": [ 378, 379, 380, 381, 382, 383, 384, 385, 466, 467, 468, 469, 470, 471, 472, 473 ] },

    { "name": "TOB-5", "feds": [ 368, 369, 370, 373, 374, 375, 413, 414, 415, 427, 428, 429 ] },

    { "name": "CTPPS_TOT", "feds": [ 577, 578, 579, 580, 581 ] },

    { "name": "TWINMUX1", "feds": [ 1390, 1391 ] },

    { "name": "TWINMUX2", "feds": [ 1393, 1394, 1395 ] },

]

#----------------------------------------------------------------------
# utility functions
#----------------------------------------------------------------------

def fedbuilderFromFed(fed):
    # find the fedbuilder the given fed belongs to
    for line in fedBuilderGroups:
        if fed in line['feds']:
            return line['name']

    # not found
    return None

#----------------------------------------------------------------------
