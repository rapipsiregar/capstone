/**
 * Real Benchmark Dataset & Brand Drivers from 8,365 Authentic Female Daily Reviews
 * 100% Empirical Data Synchronized with models and annotated dataset.
 */

const DATASET_BENCHMARK = {
  ALL: {
    total: 8365,
    highTrustPct: 48,
    topAspect: "Klaim Efikasi & Manfaat",
    aspectCounts: {
      "Klaim_Efikasi_Manfaat": 4870,
      "Kandungan_Bahan_Sensitivitas": 1686,
      "Transparansi_Layanan_Harga": 1543,
      "Sertifikasi_Halal_BPOM": 266
    },
    trustCounts: {
      "High_Trust": 4026,
      "Low_Trust": 2310,
      "Neutral": 2029
    }
  },
  Wardah: {
    total: 447,
    highTrustPct: 40,
    topAspect: "Klaim Efikasi & Manfaat",
    aspectCounts: {
      "Klaim_Efikasi_Manfaat": 274,
      "Kandungan_Bahan_Sensitivitas": 91,
      "Transparansi_Layanan_Harga": 75,
      "Sertifikasi_Halal_BPOM": 7
    },
    trustCounts: { "High_Trust": 180, "Low_Trust": 143, "Neutral": 124 }
  },
  Emina: {
    total: 213,
    highTrustPct: 46,
    topAspect: "Klaim Efikasi & Manfaat",
    aspectCounts: {
      "Klaim_Efikasi_Manfaat": 102,
      "Kandungan_Bahan_Sensitivitas": 55,
      "Transparansi_Layanan_Harga": 52,
      "Sertifikasi_Halal_BPOM": 4
    },
    trustCounts: { "High_Trust": 98, "Low_Trust": 65, "Neutral": 50 }
  },
  Safi: {
    total: 109,
    highTrustPct: 45,
    topAspect: "Klaim Efikasi & Manfaat",
    aspectCounts: {
      "Klaim_Efikasi_Manfaat": 73,
      "Kandungan_Bahan_Sensitivitas": 23,
      "Transparansi_Layanan_Harga": 11,
      "Sertifikasi_Halal_BPOM": 2
    },
    trustCounts: { "High_Trust": 49, "Low_Trust": 32, "Neutral": 28 }
  },
  "Mustika Ratu": {
    total: 128,
    highTrustPct: 50,
    topAspect: "Klaim Efikasi & Manfaat",
    aspectCounts: {
      "Klaim_Efikasi_Manfaat": 80,
      "Transparansi_Layanan_Harga": 27,
      "Kandungan_Bahan_Sensitivitas": 19,
      "Sertifikasi_Halal_BPOM": 2
    },
    trustCounts: { "High_Trust": 64, "Neutral": 33, "Low_Trust": 31 }
  }
};

/**
 * Real Empirical Feature Attribution & Brand Drivers from 8,365 Authentic Female Daily Reviews
 * 100% Mathematically Calculated: TF-IDF(word) * Model_Weights(LinearSVC / IndoBERT)
 * Zero Hardcoded Preset Points.
 */

const BRAND_DRIVERS = {
  "DEFAULT": {
    "high": [
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0106
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0105
      },
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0082
      },
      {
        "word": "pakai",
        "score": "+0.01",
        "raw_score": 0.0082
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0081
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.09",
        "raw_score": -0.0881
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0377
      },
      {
        "word": "perih",
        "score": "-0.04",
        "raw_score": -0.0376
      },
      {
        "word": "panas",
        "score": "-0.03",
        "raw_score": -0.0277
      },
      {
        "word": "merah",
        "score": "-0.02",
        "raw_score": -0.0179
      }
    ]
  },
  "Wardah": {
    "high": [
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0117
      },
      {
        "word": "gel",
        "score": "+0.01",
        "raw_score": 0.0116
      },
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0105
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.0101
      },
      {
        "word": "pakai",
        "score": "+0.01",
        "raw_score": 0.0097
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.10",
        "raw_score": -0.0964
      },
      {
        "word": "panas",
        "score": "-0.06",
        "raw_score": -0.062
      },
      {
        "word": "perih",
        "score": "-0.04",
        "raw_score": -0.0358
      },
      {
        "word": "iritasi",
        "score": "-0.03",
        "raw_score": -0.0349
      },
      {
        "word": "tidak cocok",
        "score": "-0.02",
        "raw_score": -0.0156
      }
    ]
  },
  "The Body Shop": {
    "high": [
      {
        "word": "jual",
        "score": "+0.01",
        "raw_score": 0.0146
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0112
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0098
      },
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0091
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.0088
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.11",
        "raw_score": -0.1127
      },
      {
        "word": "perih",
        "score": "-0.06",
        "raw_score": -0.0645
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0446
      },
      {
        "word": "panas",
        "score": "-0.02",
        "raw_score": -0.0226
      },
      {
        "word": "merah",
        "score": "-0.01",
        "raw_score": -0.013
      }
    ]
  },
  "Garnier": {
    "high": [
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0144
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.011
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0104
      },
      {
        "word": "wajah",
        "score": "+0.01",
        "raw_score": 0.009
      },
      {
        "word": "cerah",
        "score": "+0.01",
        "raw_score": 0.0088
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.11",
        "raw_score": -0.1059
      },
      {
        "word": "panas",
        "score": "-0.09",
        "raw_score": -0.0914
      },
      {
        "word": "perih",
        "score": "-0.05",
        "raw_score": -0.0478
      },
      {
        "word": "merah",
        "score": "-0.04",
        "raw_score": -0.0374
      },
      {
        "word": "iritasi",
        "score": "-0.03",
        "raw_score": -0.0346
      }
    ]
  },
  "Innisfree": {
    "high": [
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0108
      },
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0106
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0103
      },
      {
        "word": "innisfree",
        "score": "+0.01",
        "raw_score": 0.0095
      },
      {
        "word": "jual",
        "score": "+0.01",
        "raw_score": 0.0091
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.08",
        "raw_score": -0.0847
      },
      {
        "word": "iritasi",
        "score": "-0.05",
        "raw_score": -0.0464
      },
      {
        "word": "merah",
        "score": "-0.02",
        "raw_score": -0.024
      },
      {
        "word": "panas",
        "score": "-0.02",
        "raw_score": -0.0223
      },
      {
        "word": "kemerahan",
        "score": "-0.02",
        "raw_score": -0.0206
      }
    ]
  },
  "Pond's": {
    "high": [
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0113
      },
      {
        "word": "pakai",
        "score": "+0.01",
        "raw_score": 0.01
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0098
      },
      {
        "word": "wajah",
        "score": "+0.01",
        "raw_score": 0.0088
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.0085
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.06",
        "raw_score": -0.0597
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0444
      },
      {
        "word": "panas",
        "score": "-0.04",
        "raw_score": -0.0427
      },
      {
        "word": "perih",
        "score": "-0.04",
        "raw_score": -0.0407
      },
      {
        "word": "merah",
        "score": "-0.02",
        "raw_score": -0.0225
      }
    ]
  },
  "Viva Cosmetics": {
    "high": [
      {
        "word": "skincare",
        "score": "+0.02",
        "raw_score": 0.0162
      },
      {
        "word": "cleanser",
        "score": "+0.02",
        "raw_score": 0.0155
      },
      {
        "word": "viva",
        "score": "+0.02",
        "raw_score": 0.0153
      },
      {
        "word": "pakai",
        "score": "+0.01",
        "raw_score": 0.0112
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.0105
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.10",
        "raw_score": -0.0958
      },
      {
        "word": "perih",
        "score": "-0.05",
        "raw_score": -0.048
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0375
      },
      {
        "word": "panas",
        "score": "-0.03",
        "raw_score": -0.0261
      },
      {
        "word": "merah",
        "score": "-0.01",
        "raw_score": -0.0136
      }
    ]
  },
  "Emina": {
    "high": [
      {
        "word": "emina",
        "score": "+0.02",
        "raw_score": 0.0211
      },
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0134
      },
      {
        "word": "gel",
        "score": "+0.01",
        "raw_score": 0.0114
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0113
      },
      {
        "word": "lembab",
        "score": "+0.01",
        "raw_score": 0.0109
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.14",
        "raw_score": -0.1442
      },
      {
        "word": "perih",
        "score": "-0.05",
        "raw_score": -0.0513
      },
      {
        "word": "iritasi",
        "score": "-0.05",
        "raw_score": -0.0452
      },
      {
        "word": "panas",
        "score": "-0.03",
        "raw_score": -0.0286
      },
      {
        "word": "iritasi breakout",
        "score": "-0.01",
        "raw_score": -0.0125
      }
    ]
  },
  "Laneige": {
    "high": [
      {
        "word": "lembab",
        "score": "+0.02",
        "raw_score": 0.0185
      },
      {
        "word": "glowing",
        "score": "+0.02",
        "raw_score": 0.016
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0143
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0124
      },
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0123
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.04",
        "raw_score": -0.0428
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0377
      },
      {
        "word": "perih",
        "score": "-0.02",
        "raw_score": -0.0168
      },
      {
        "word": "bikin",
        "score": "-0.01",
        "raw_score": -0.012
      },
      {
        "word": "pecah",
        "score": "-0.01",
        "raw_score": -0.0113
      }
    ]
  },
  "Biore": {
    "high": [
      {
        "word": "sunscreen",
        "score": "+0.01",
        "raw_score": 0.0103
      },
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0103
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0101
      },
      {
        "word": "oil",
        "score": "+0.01",
        "raw_score": 0.0086
      },
      {
        "word": "spf",
        "score": "+0.01",
        "raw_score": 0.0081
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.05",
        "raw_score": -0.049
      },
      {
        "word": "perih",
        "score": "-0.04",
        "raw_score": -0.0425
      },
      {
        "word": "iritasi",
        "score": "-0.03",
        "raw_score": -0.0315
      },
      {
        "word": "komedo",
        "score": "-0.02",
        "raw_score": -0.0172
      },
      {
        "word": "panas",
        "score": "-0.01",
        "raw_score": -0.0147
      }
    ]
  },
  "Cosrx": {
    "high": [
      {
        "word": "jual",
        "score": "+0.02",
        "raw_score": 0.0236
      },
      {
        "word": "skincare",
        "score": "+0.02",
        "raw_score": 0.0157
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0113
      },
      {
        "word": "moisturizer",
        "score": "+0.01",
        "raw_score": 0.0109
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.0107
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.14",
        "raw_score": -0.1415
      },
      {
        "word": "iritasi",
        "score": "-0.06",
        "raw_score": -0.0551
      },
      {
        "word": "merah",
        "score": "-0.02",
        "raw_score": -0.0225
      },
      {
        "word": "iritasi breakout",
        "score": "-0.02",
        "raw_score": -0.0194
      },
      {
        "word": "breakout",
        "score": "-0.02",
        "raw_score": -0.0194
      }
    ]
  },
  "Hada Labo": {
    "high": [
      {
        "word": "hydrating",
        "score": "+0.02",
        "raw_score": 0.0152
      },
      {
        "word": "jual",
        "score": "+0.01",
        "raw_score": 0.0149
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0131
      },
      {
        "word": "lembab",
        "score": "+0.01",
        "raw_score": 0.0118
      },
      {
        "word": "kulitku",
        "score": "+0.01",
        "raw_score": 0.0095
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.13",
        "raw_score": -0.1259
      },
      {
        "word": "iritasi",
        "score": "-0.03",
        "raw_score": -0.0298
      },
      {
        "word": "perih",
        "score": "-0.03",
        "raw_score": -0.0262
      },
      {
        "word": "tidak cocok",
        "score": "-0.01",
        "raw_score": -0.0139
      },
      {
        "word": "bikin",
        "score": "-0.01",
        "raw_score": -0.0135
      }
    ]
  },
  "NIVEA": {
    "high": [
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0127
      },
      {
        "word": "oil",
        "score": "+0.01",
        "raw_score": 0.0113
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.011
      },
      {
        "word": "micellar",
        "score": "+0.01",
        "raw_score": 0.0109
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0108
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.10",
        "raw_score": -0.1024
      },
      {
        "word": "iritasi",
        "score": "-0.06",
        "raw_score": -0.0642
      },
      {
        "word": "perih",
        "score": "-0.05",
        "raw_score": -0.0519
      },
      {
        "word": "panas",
        "score": "-0.04",
        "raw_score": -0.0427
      },
      {
        "word": "breakout",
        "score": "-0.02",
        "raw_score": -0.0206
      }
    ]
  },
  "Mustika Ratu": {
    "high": [
      {
        "word": "kulit",
        "score": "+0.02",
        "raw_score": 0.0205
      },
      {
        "word": "suka",
        "score": "+0.02",
        "raw_score": 0.0165
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0141
      },
      {
        "word": "lembab",
        "score": "+0.01",
        "raw_score": 0.0109
      },
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0099
      }
    ],
    "low": [
      {
        "word": "iritasi",
        "score": "-0.05",
        "raw_score": -0.0474
      },
      {
        "word": "panas",
        "score": "-0.04",
        "raw_score": -0.0352
      },
      {
        "word": "perih",
        "score": "-0.02",
        "raw_score": -0.02
      },
      {
        "word": "beruntusan",
        "score": "-0.02",
        "raw_score": -0.018
      },
      {
        "word": "iritasi breakout",
        "score": "-0.01",
        "raw_score": -0.0132
      }
    ]
  },
  "FREEMAN": {
    "high": [
      {
        "word": "suka",
        "score": "+0.02",
        "raw_score": 0.0168
      },
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0119
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0115
      },
      {
        "word": "wajah",
        "score": "+0.01",
        "raw_score": 0.0106
      },
      {
        "word": "freeman",
        "score": "+0.01",
        "raw_score": 0.0092
      }
    ],
    "low": [
      {
        "word": "perih",
        "score": "-0.12",
        "raw_score": -0.1186
      },
      {
        "word": "panas",
        "score": "-0.08",
        "raw_score": -0.0764
      },
      {
        "word": "iritasi",
        "score": "-0.05",
        "raw_score": -0.0517
      },
      {
        "word": "beruntusan",
        "score": "-0.03",
        "raw_score": -0.0287
      },
      {
        "word": "merah",
        "score": "-0.02",
        "raw_score": -0.0248
      }
    ]
  },
  "Kiehl's": {
    "high": [
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0122
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0121
      },
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0111
      },
      {
        "word": "glowing",
        "score": "+0.01",
        "raw_score": 0.0105
      },
      {
        "word": "bagus banget",
        "score": "+0.01",
        "raw_score": 0.0091
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.07",
        "raw_score": -0.0701
      },
      {
        "word": "iritasi",
        "score": "-0.03",
        "raw_score": -0.0347
      },
      {
        "word": "perih",
        "score": "-0.02",
        "raw_score": -0.0231
      },
      {
        "word": "mata",
        "score": "-0.02",
        "raw_score": -0.0171
      },
      {
        "word": "iritasi breakout",
        "score": "-0.02",
        "raw_score": -0.0156
      }
    ]
  },
  "Safi": {
    "high": [
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0129
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0127
      },
      {
        "word": "glowing",
        "score": "+0.01",
        "raw_score": 0.0103
      },
      {
        "word": "bekas",
        "score": "+0.01",
        "raw_score": 0.0101
      },
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0091
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.13",
        "raw_score": -0.1253
      },
      {
        "word": "iritasi",
        "score": "-0.06",
        "raw_score": -0.0553
      },
      {
        "word": "merah",
        "score": "-0.04",
        "raw_score": -0.0405
      },
      {
        "word": "perih",
        "score": "-0.04",
        "raw_score": -0.0399
      },
      {
        "word": "panas",
        "score": "-0.03",
        "raw_score": -0.034
      }
    ]
  },
  "Nature Republic": {
    "high": [
      {
        "word": "suka",
        "score": "+0.02",
        "raw_score": 0.0191
      },
      {
        "word": "gel",
        "score": "+0.02",
        "raw_score": 0.0175
      },
      {
        "word": "natrep",
        "score": "+0.02",
        "raw_score": 0.0163
      },
      {
        "word": "lembab",
        "score": "+0.01",
        "raw_score": 0.014
      },
      {
        "word": "sheet",
        "score": "+0.01",
        "raw_score": 0.012
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.10",
        "raw_score": -0.0967
      },
      {
        "word": "panas",
        "score": "-0.05",
        "raw_score": -0.0538
      },
      {
        "word": "merah",
        "score": "-0.05",
        "raw_score": -0.0529
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0381
      },
      {
        "word": "bikin",
        "score": "-0.01",
        "raw_score": -0.0138
      }
    ]
  },
  "SK-II": {
    "high": [
      {
        "word": "glowing",
        "score": "+0.02",
        "raw_score": 0.0196
      },
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0137
      },
      {
        "word": "fte",
        "score": "+0.01",
        "raw_score": 0.0128
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0111
      },
      {
        "word": "pakai",
        "score": "+0.01",
        "raw_score": 0.011
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.08",
        "raw_score": -0.077
      },
      {
        "word": "tidak cocok",
        "score": "-0.02",
        "raw_score": -0.0154
      },
      {
        "word": "merah",
        "score": "-0.01",
        "raw_score": -0.0139
      },
      {
        "word": "padahal",
        "score": "-0.01",
        "raw_score": -0.0123
      },
      {
        "word": "skii",
        "score": "-0.01",
        "raw_score": -0.0108
      }
    ]
  },
  "Sariayu": {
    "high": [
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0144
      },
      {
        "word": "suka",
        "score": "+0.01",
        "raw_score": 0.0125
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0115
      },
      {
        "word": "lotion",
        "score": "+0.01",
        "raw_score": 0.0094
      },
      {
        "word": "pakai",
        "score": "+0.01",
        "raw_score": 0.0091
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.12",
        "raw_score": -0.1211
      },
      {
        "word": "panas",
        "score": "-0.06",
        "raw_score": -0.0605
      },
      {
        "word": "perih",
        "score": "-0.05",
        "raw_score": -0.0529
      },
      {
        "word": "iritasi",
        "score": "-0.05",
        "raw_score": -0.047
      },
      {
        "word": "merah",
        "score": "-0.04",
        "raw_score": -0.0375
      }
    ]
  },
  "L'Oreal Paris": {
    "high": [
      {
        "word": "sunscreen",
        "score": "+0.02",
        "raw_score": 0.0182
      },
      {
        "word": "suka",
        "score": "+0.02",
        "raw_score": 0.0175
      },
      {
        "word": "jual",
        "score": "+0.01",
        "raw_score": 0.0131
      },
      {
        "word": "glowing",
        "score": "+0.01",
        "raw_score": 0.0129
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0119
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.07",
        "raw_score": -0.0684
      },
      {
        "word": "perih",
        "score": "-0.05",
        "raw_score": -0.0451
      },
      {
        "word": "merah",
        "score": "-0.02",
        "raw_score": -0.0224
      },
      {
        "word": "iritasi",
        "score": "-0.02",
        "raw_score": -0.0216
      },
      {
        "word": "susah",
        "score": "-0.01",
        "raw_score": -0.0137
      }
    ]
  },
  "Some by Mi": {
    "high": [
      {
        "word": "jual",
        "score": "+0.02",
        "raw_score": 0.0231
      },
      {
        "word": "bekas",
        "score": "+0.02",
        "raw_score": 0.0183
      },
      {
        "word": "serum",
        "score": "+0.02",
        "raw_score": 0.0153
      },
      {
        "word": "glowing",
        "score": "+0.01",
        "raw_score": 0.0126
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0111
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.06",
        "raw_score": -0.0632
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0375
      },
      {
        "word": "malah",
        "score": "-0.01",
        "raw_score": -0.0137
      },
      {
        "word": "tidak cocok",
        "score": "-0.01",
        "raw_score": -0.0135
      },
      {
        "word": "iritasi breakout",
        "score": "-0.01",
        "raw_score": -0.0133
      }
    ]
  },
  "Acnes": {
    "high": [
      {
        "word": "bekas",
        "score": "+0.02",
        "raw_score": 0.0223
      },
      {
        "word": "acnes",
        "score": "+0.02",
        "raw_score": 0.0175
      },
      {
        "word": "gel",
        "score": "+0.01",
        "raw_score": 0.0137
      },
      {
        "word": "skincare",
        "score": "+0.01",
        "raw_score": 0.0128
      },
      {
        "word": "warnanya",
        "score": "+0.01",
        "raw_score": 0.0086
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.18",
        "raw_score": -0.1798
      },
      {
        "word": "perih",
        "score": "-0.10",
        "raw_score": -0.0975
      },
      {
        "word": "iritasi",
        "score": "-0.03",
        "raw_score": -0.0319
      },
      {
        "word": "merah",
        "score": "-0.02",
        "raw_score": -0.0236
      },
      {
        "word": "jerawat",
        "score": "-0.02",
        "raw_score": -0.02
      }
    ]
  },
  "PURIVERA BOTANICALS": {
    "high": [
      {
        "word": "oil",
        "score": "+0.05",
        "raw_score": 0.053
      },
      {
        "word": "face",
        "score": "+0.03",
        "raw_score": 0.0271
      },
      {
        "word": "rosehip",
        "score": "+0.02",
        "raw_score": 0.0178
      },
      {
        "word": "bekas",
        "score": "+0.02",
        "raw_score": 0.0178
      },
      {
        "word": "face oil",
        "score": "+0.02",
        "raw_score": 0.016
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.18",
        "raw_score": -0.1809
      },
      {
        "word": "kemerahan",
        "score": "-0.03",
        "raw_score": -0.0321
      },
      {
        "word": "iritasi",
        "score": "-0.03",
        "raw_score": -0.0291
      },
      {
        "word": "merah",
        "score": "-0.02",
        "raw_score": -0.0244
      },
      {
        "word": "tidak cocok",
        "score": "-0.02",
        "raw_score": -0.02
      }
    ]
  },
  "The Ordinary": {
    "high": [
      {
        "word": "bekas",
        "score": "+0.03",
        "raw_score": 0.0255
      },
      {
        "word": "jual",
        "score": "+0.02",
        "raw_score": 0.0244
      },
      {
        "word": "minat",
        "score": "+0.01",
        "raw_score": 0.0137
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0126
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.0103
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.13",
        "raw_score": -0.1252
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0383
      },
      {
        "word": "perih",
        "score": "-0.02",
        "raw_score": -0.0231
      },
      {
        "word": "padahal",
        "score": "-0.02",
        "raw_score": -0.0166
      },
      {
        "word": "iritasi breakout",
        "score": "-0.01",
        "raw_score": -0.0126
      }
    ]
  },
  "Mediheal": {
    "high": [
      {
        "word": "mediheal",
        "score": "+0.06",
        "raw_score": 0.0563
      },
      {
        "word": "sheet",
        "score": "+0.02",
        "raw_score": 0.0245
      },
      {
        "word": "sheetmask",
        "score": "+0.02",
        "raw_score": 0.0225
      },
      {
        "word": "lembab",
        "score": "+0.02",
        "raw_score": 0.0223
      },
      {
        "word": "bener",
        "score": "+0.02",
        "raw_score": 0.018
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.11",
        "raw_score": -0.112
      },
      {
        "word": "iritasi",
        "score": "-0.02",
        "raw_score": -0.022
      },
      {
        "word": "panas",
        "score": "-0.01",
        "raw_score": -0.0133
      },
      {
        "word": "padahal",
        "score": "-0.01",
        "raw_score": -0.0107
      },
      {
        "word": "bikin",
        "score": "-0.01",
        "raw_score": -0.0103
      }
    ]
  },
  "Skin Aqua": {
    "high": [
      {
        "word": "spf",
        "score": "+0.07",
        "raw_score": 0.069
      },
      {
        "word": "sunscreen",
        "score": "+0.03",
        "raw_score": 0.0263
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0124
      },
      {
        "word": "whitecast",
        "score": "+0.01",
        "raw_score": 0.012
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.0119
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.09",
        "raw_score": -0.0944
      },
      {
        "word": "iritasi",
        "score": "-0.03",
        "raw_score": -0.0349
      },
      {
        "word": "merah",
        "score": "-0.03",
        "raw_score": -0.0289
      },
      {
        "word": "bikin",
        "score": "-0.02",
        "raw_score": -0.0166
      },
      {
        "word": "breakout",
        "score": "-0.02",
        "raw_score": -0.0157
      }
    ]
  },
  "Benton": {
    "high": [
      {
        "word": "jual",
        "score": "+0.02",
        "raw_score": 0.0221
      },
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0128
      },
      {
        "word": "cocok",
        "score": "+0.01",
        "raw_score": 0.012
      },
      {
        "word": "gel",
        "score": "+0.01",
        "raw_score": 0.0114
      },
      {
        "word": "bagus banget",
        "score": "+0.01",
        "raw_score": 0.0102
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.14",
        "raw_score": -0.137
      },
      {
        "word": "iritasi",
        "score": "-0.10",
        "raw_score": -0.1015
      },
      {
        "word": "iritasi breakout",
        "score": "-0.05",
        "raw_score": -0.0456
      },
      {
        "word": "breakout",
        "score": "-0.05",
        "raw_score": -0.0456
      },
      {
        "word": "tidak cocok",
        "score": "-0.02",
        "raw_score": -0.0207
      }
    ]
  },
  "Clean And Clear": {
    "high": [
      {
        "word": "cocok",
        "score": "+0.02",
        "raw_score": 0.0192
      },
      {
        "word": "cocok banget",
        "score": "+0.01",
        "raw_score": 0.0114
      },
      {
        "word": "bener",
        "score": "+0.01",
        "raw_score": 0.0113
      },
      {
        "word": "enak",
        "score": "+0.01",
        "raw_score": 0.0103
      },
      {
        "word": "aku cocok",
        "score": "+0.01",
        "raw_score": 0.01
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.09",
        "raw_score": -0.0874
      },
      {
        "word": "panas",
        "score": "-0.03",
        "raw_score": -0.0346
      },
      {
        "word": "merah",
        "score": "-0.03",
        "raw_score": -0.0299
      },
      {
        "word": "tidak cocok",
        "score": "-0.03",
        "raw_score": -0.0268
      },
      {
        "word": "perih",
        "score": "-0.02",
        "raw_score": -0.0219
      }
    ]
  },
  "Ovale": {
    "high": [
      {
        "word": "kulit",
        "score": "+0.01",
        "raw_score": 0.0097
      },
      {
        "word": "micellar",
        "score": "+0.01",
        "raw_score": 0.0095
      },
      {
        "word": "wajah",
        "score": "+0.01",
        "raw_score": 0.0089
      },
      {
        "word": "bagus",
        "score": "+0.01",
        "raw_score": 0.008
      },
      {
        "word": "pakai",
        "score": "+0.01",
        "raw_score": 0.0074
      }
    ],
    "low": [
      {
        "word": "perih",
        "score": "-0.12",
        "raw_score": -0.1243
      },
      {
        "word": "panas",
        "score": "-0.12",
        "raw_score": -0.1183
      },
      {
        "word": "beruntusan",
        "score": "-0.10",
        "raw_score": -0.095
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0396
      },
      {
        "word": "merah",
        "score": "-0.03",
        "raw_score": -0.0346
      }
    ]
  },
  "Haple": {
    "high": [
      {
        "word": "oil",
        "score": "+0.03",
        "raw_score": 0.0341
      },
      {
        "word": "face",
        "score": "+0.03",
        "raw_score": 0.0306
      },
      {
        "word": "bekas",
        "score": "+0.02",
        "raw_score": 0.0203
      },
      {
        "word": "bener",
        "score": "+0.02",
        "raw_score": 0.0164
      },
      {
        "word": "face oil",
        "score": "+0.01",
        "raw_score": 0.0147
      }
    ],
    "low": [
      {
        "word": "beruntusan",
        "score": "-0.08",
        "raw_score": -0.0798
      },
      {
        "word": "merah",
        "score": "-0.04",
        "raw_score": -0.0377
      },
      {
        "word": "iritasi",
        "score": "-0.04",
        "raw_score": -0.0352
      },
      {
        "word": "perih",
        "score": "-0.03",
        "raw_score": -0.0261
      },
      {
        "word": "oil ini",
        "score": "-0.01",
        "raw_score": -0.0136
      }
    ]
  }
};
