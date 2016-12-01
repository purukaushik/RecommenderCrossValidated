## Usage
0. If a topic doesn't exist in the database, you get an empty json like this
  ```json
    {
    "related_topics": [],
    "topic": "lik"
  }
  ```
1. Collab filtering metrics for a topic=likert

  ```bash
    curl http://ec2-52-43-158-164.us-west-2.compute.amazonaws.com:3000/collabf?topic=likert
  ```
  returns all related topics to `likert` obtained using collaborative filtering.
  Result looks like:
  ```json
  {
  "related_topics": [
    [
      {
        "name": "likert",
        "value": 1.0
      },
      {
        "name": "nnet",
        "value": 0.0
      },
      {
        "name": "biostatistics",
        "value": 0.0
      },
      {
        "name": "metric",
        "value": 0.0288795491
      },
      {
        "name": "repeatability",
        "value": 0.0
      },
      {
        "name": "ggplot2",
        "value": 0.0
      },
      {
        "name": "regression",
        "value": 0.192957514
      },
      {
        "name": "mancova",
        "value": 0.0
      },
      {
        "name": "caret",
        "value": 0.0674199862
      },
      {
        "name": "information",
        "value": 0.1272462204
      },
      {
        "name": "stationarity",
        "value": 0.0
      },
      {
        "name": "hotelling",
        "value": 0.0
      },
      {
        "name": "apriori",
        "value": 0.0
      },
      {
        "name": "microarray",
        "value": 0.0402911482
      },
      {
        "name": "academia",
        "value": 0.0
      },
      {
        "name": "gibbs",
        "value": 0.0
      },
      {
        "name": "units",
        "value": 0.1732149228
      },
      {
        "name": "multivariable",
        "value": 0.0
      },
      {
        "name": "ecm",
        "value": 0.0
      },
      {
        "name": "determinant",
        "value": 0.0
      },
      {
        "name": "mplus",
        "value": 0.0
      },
      {
        "name": "jmp",
        "value": 0.0
      },
      {
        "name": "error",
        "value": 0.1820168541
      },
      {
        "name": "covariance",
        "value": 0.0945328086
      },
      {
        "name": "binning",
        "value": 0.0489115988
      },
      {
        "name": "gam",
        "value": 0.0
      },
      {
        "name": "representative",
        "value": 0.0489115988
      },
      {
        "name": "systematic",
        "value": 0.0550481883
      },
      {
        "name": "bayesian",
        "value": 0.0597919443
      },
      {
        "name": "robust",
        "value": 0.1175413598
      },
      {
        "name": "invariance",
        "value": 0.0
      },
      {
        "name": "white-noise",
        "value": 0.2079879994
      },
      {
        "name": "normalization",
        "value": 0.0235440805
      },
      {
        "name": "cointegration",
        "value": 0.0
      },
      {
        "name": "concordance",
        "value": 0.0
      },
      {
        "name": "endogeneity",
        "value": 0.0
      },
        {
          "name": "pymc",
          "value": 0.0
        },
        {
          "name": "exponential",
          "value": 0.1192288313
        },
        {
          "name": "database",
          "value": 0.0
        },
        {
          "name": "underdetermined",
          "value": 0.0
        },
        {
          "name": "rbm",
          "value": 0.0
        },
        {
          "name": "optimization",
          "value": 0.0624902367
        },
        {
          "name": "consistency",
          "value": 0.0262431941
        },
        {
          "name": "statsmodels",
          "value": 0.0
        },
        {
          "name": "untagged",
          "value": 0.2012072449
        },
        {
          "name": "model",
          "value": 0.2089937136
        },
        {
          "name": "estimation",
          "value": 0.0313496568
        },
        {
          "name": "wilcoxon",
          "value": 0.218771804
        },
        {
          "name": "aic",
          "value": 0.2026801461
        }
      ]
    ],
    "topic": "likert"
  }
  ```

2. Content based cosine similarities for a topic=likert
  ```bash
    curl 
  ```
  returns all related topics to topic `likert` based on cosine similarity.
  Output looks like this:
  ```json
    {
    "related_topics": [
      [
        {
          "name": "invariance",
          "value": 0.0
        },
        {
          "name": "likert",
          "value": 1.0
        },
        {
          "name": "nnet",
          "value": 0.0
        },
        {
          "name": "biostatistics",
          "value": 0.0
        },
        {
          "name": "metric",
          "value": 0.0
        },
        {
          "name": "repeatability",
          "value": 0.0
        },
        {
          "name": "ggplot2",
          "value": 0.0
        },
        {
          "name": "regression",
          "value": 0.03486487
        },
        {
        "name": "mancova",
        "value": 0.0
      },
      {
        "name": "caret",
        "value": 0.0
      },
      {
        "name": "information",
        "value": 0.0172825282
      },
      {
        "name": "stationarity",
        "value": 0.0
      },
      {
        "name": "hotelling",
        "value": 0.0
      },
      {
        "name": "apriori",
        "value": 0.0
      },
      {
        "name": "endogeneity",
        "value": 0.0
      },
      {
        "name": "microarray",
        "value": 0.0
      },
      {
        "name": "academia",
        "value": 0.0
      },
      {
        "name": "gibbs",
        "value": 0.0
      },
      {
        "name": "units",
        "value": 0.0511269895
      },
      {
        "name": "mplus",
        "value": 0.0
      },
      {
        "name": "ecm",
        "value": 0.0
      },
      {
        "name": "determinant",
        "value": 0.0
      },
      {
        "name": "jmp",
        "value": 0.0
      },
      {
        "name": "consistency",
        "value": 0.0
      },
      {
        "name": "covariance",
        "value": 0.0
      },
      {
        "name": "binning",
        "value": 0.0
      },
      {
        "name": "gam",
        "value": 0.0
      },
      {
        "name": "representative",
        "value": 0.0
      },
      {
        "name": "systematic",
        "value": 0.0
      },
      {
        "name": "bayesian",
        "value": 0.0
      },
      {
        "name": "robust",
        "value": 0.0
      },
      {
        "name": "multivariable",
        "value": 0.0
      },
      {
        "name": "white-noise",
        "value": 0.0794353246
      },
      {
        "name": "normalization",
        "value": 0.0
      },
      {
        "name": "cointegration",
        "value": 0.0
      },
      {
        "name": "concordance",
        "value": 0.0
      },
      {
        "name": "underdetermined",
        "value": 0.0
      },
      {
        "name": "pymc",
        "value": 0.0
      },
      {
        "name": "exponential",
        "value": 0.0
      },
      {
        "name": "database",
        "value": 0.0
      },
      {
        "name": "rbm",
        "value": 0.0
      },
      {
        "name": "optimization",
        "value": 0.0
      },
      {
        "name": "error",
        "value": 0.0130277265
      },
      {
        "name": "statsmodels",
        "value": 0.0
      },
      {
        "name": "untagged",
        "value": 0.0632060618
      },
      {
        "name": "model",
        "value": 0.0532246295
      },
      {
        "name": "estimation",
        "value": 0.0
      },
      {
        "name": "wilcoxon",
        "value": 0.0837952868
      },
      {
        "name": "aic",
        "value": 0.0366617788
      }
    ]
  ],
  "topic": "likert"
}
  ```
