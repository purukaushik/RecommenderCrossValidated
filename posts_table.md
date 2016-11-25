Example json
``` json
{
	"data": [{
			//---------QUESTION DATA ----------
			"_id": "5838b73d10c7c46ef6a7f072",
			"View_count": 251,
			"Display_name": "Steven Stewart-Gallus",
			"Question_score": 5,
			"Question_content": "The correlation coefficient is: r = \\frac{\\sum_k \\frac{(x_k - \\bar{x}) (y_k - \\bar{y_k})}{s_x s_y}}{n-1} The sample mean and the sample standard deviation are sensitive to outliers.As well, the mechanism where, r = \\frac{\\sum_k \\text{stuff}_k}{n -1} is sort of like a mean as well and maybe there might be a variation on that which is less sensitive to variation.The sample mean is: \\bar{x} = \\frac{\\sum_k x_k}{n} The sample standard deviation is: s_x = \\sqrt{\\frac{\\sum_k (x_k - \\bar{x})^2}{n -1}} I think I wantThe median: \\text{Median}[x]The median absolute deviation: \\text{Median}[\\lvert x - \\text{Median}[x]\\rvert] And for the correlation: \\text{Median}\\left[\\frac{(x -\\text{Median}[x])(y-\\text{Median}[y]) }{\\text{Median}[\\lvert x - \\text{Median}[x]\\rvert]\\text{Median}[\\lvert y - \\text{Median}[y]\\rvert]}\\right] I tried this with some random numbers but got results greater than 1 which seems wrong. See the following R code. x&lt;- c(237, 241, 251, 254, 263) y&lt;- c(216, 218, 227, 234, 235) median.x &lt;- median(x) median.y &lt;- median(y) mad.x &lt;- median(abs(x - median.x)) mad.y &lt;- median(abs(y - median.y)) r &lt;- median((((x - median.x) * (y - median.y)) / (mad.x * mad.y))) print(r) ## Prints 1.125 plot(x,y)",
			"Creater_id": 111109,
			"Start_date": "2016-11-14 14:08:50",
			"Question_id": 245931,
			"Tags": [
				"regression",
				"correlation",
				"median",
				"mad"
			],
			"Answer_count": 4,
			"Last_activity": "2016-11-19 09:13:59",
			"Link": "http://stats.stackexchange.com/questions/245931/is-there-a-version-of-the-correlation-coefficient-that-is-less-sensitive-to-outl",
			"Creator_reputation": 166,


			//list of answers
			"answers":

				[{
					"_id": "5838b73d10c7c46ef6a7f073",
					"Last_activity": "2016-11-19 09:13:59",
					"Creator_reputation": 14047,
					"Question_score": 1,
					"Answer_content": "My answer premises that the OP does not already know what observations are outliers because if the OP did then data adjustments would be obvious. Thus part of my answer deals with identification of the outlier(s)When you construct an OLS model ( versus ), you get a regression coefficient and subsequently the correlation coefficient I think it may be inherently dangerous not to challenge the \"givens\" . In this way you understand that the regression coefficient and its sibling are premised on no outliers/unusual values. Now if you identify an outlier and add an appropriate 0/1 predictor to your regression model the resultant regression coefficient for the  is now robustified to the outlier/anomaly. This regression coefficient for the  is then \"truer\" than the original regression coefficient as it is uncontaminated by the identified outlier. Note that no observations get permanently \"thrown away\"; it's just that an adjustment for the  value is implicit for the point of the anomaly.  This new coefficient for the  can then be converted to a robust . An alternative view of this is just to take the adjusted  value and replace the original  value with this \"smoothed value\" and then run a simple correlation.This process would have to be done repetitively until no outlier is found.I hope this clarification helps the down-voters to understand the suggested procedure . Thanks to whuber for pushing me for clarification. If anyone still needs help with this one can always simulate a  data set and inject an outlier at any particular x and follow the suggested steps to obtain a better estimate of . I welcome any comments on this as if it is \"incorrect\" I would sincerely like to know why hopefully supported by a numerical counter-example.EDITED TO PRESENT A SIMPLE EXAMPLE :A small example will suffice to illustrate the proposed/transparent method of “obtaining  of a version of r that is less sensitive to outliers”  which is the direct question of the OP.  This is an easy to follow script using standard ols and some simple arithmetic . Recall that B the ols regression coefficient is equal to r*[sigmay/sigmax).Consider the following 10 pairs of observations.And graphically The simple correlation coefficient is .75  with sigmay = 18.41 and sigmax=.38Now we compute a regression between y and x and obtain the followingWhere  36.538 = .75*[18.41/.38]  = r*[sigmay/sigmax]The actual/fit table suggests an initial estimate  of an outlier at observation 5 with value of 32.799 . If  we exclude the 5th point  we obtain the following regression resultWhich yields a prediction of 173.31 using the x value 13.61 . This prediction then suggests a refined estimate of the outlier to be as follows  ;  209-173.31 = 35.69 .If we now restore the original 10 values but replace the value of y at period 5 (209) by the estimated/cleansed value 173.31 we obtain and Recomputed r we get the value .98 from the regression equationr=  B*[sigmax/sigmay].98  = [37.4792]*[ .38/14.71]  Thus we now have a version or r (r =.98) that is less sensitive to an identified outlier at observation 5 .  N.B. that the sigmay used above (14.71) is based on the adjusted y at period 5 and not the original contaminated sigmay (18.41). The effect of the outlier is large due to it's estimated size and the sample size. What we had was 9 pairs of readings (1-4;6-10) that were highly correlated but the standard r was obfuscated/distorted by the outlier at obervation 5.There is a less transparent but nore powerfiul approach to resolving this and that is to use the TSAY procedure http://docplayer.net/12080848-Outliers-level-shifts-and-variance-changes-in-time-series.html  to search for and resolve any and all outliers in one pass. For example  suggsts that the outlier value is 36.4481 thus the adjusted value (one-sided) is 172.5419 . Similar output would generate an actual/cleansed graph or table.  . Tsay's procedure actually iterativel checks each and every point for \" statistical importance\" and then selects the best point requiring adjustment. Time series solutions are immediately applicable if there is no time structure evidented or potentially assumed in the data. What I did was to supress the incorporation of any time series filter as I had domain knowledge/\"knew\" that it was captured in a cross-sectional i.e.non-longitudinal manner.",
					"Display_name": "IrishStat",
					"Creater_id": 3382,
					"Start_date": "2016-11-14 14:32:55",
					"Question_id": 245931
				}, {
					"_id": "5838b73d10c7c46ef6a7f074",
					"Last_activity": "2016-11-18 09:14:16",
					"Creator_reputation": 316,
					"Question_score": 2,
					"Answer_content": "This is a solution which works well for the data and problem proposed by IrishStat. Y=ax+b+eThe idea is to replace the sample variance of  by the predicted variance \\sigma_Y^2=a^2\\sigma_x^2+\\sigma_e^2. so that the formula for the correlation becomes r=\\sqrt{\\frac{a^2\\sigma^2_x}{a^2\\sigma_x^2+\\sigma_e^2}}Now the reason that the correlation is underestimated is that the outlier causes the estimate for  to be inflated.To deal with this replace the assumption of normally distributed errors inthe regression with a normal mixture\\frac{0.95}{\\sqrt{2\\pi} \\sigma} \\exp(-\\frac{e^2}{2\\sigma^2})+\\frac{0.05}{\\sqrt{2\\pi} 3\\sigma} \\exp(-\\frac{e^2}{18\\sigma^2}) I first saw this distribution used for robustness in Hubers book, Robust Statistics.This is \"moderately\" robust and works well for this example. It also hasthe property that if there are no outliers it produces parameter estimates almost identical to the usual least squares ones. So this procedure implicitly removes the influence of the outlier without having to modify the data.   Fitting the data produces a correlation estimate of 0.944812.",
					"Display_name": "dave fournier",
					"Creater_id": 86720,
					"Start_date": "2016-11-18 09:14:16",
					"Question_id": 245931
				}, {
					"_id": "5838b73d10c7c46ef6a7f075",
					"Last_activity": "2016-11-15 12:39:21",
					"Creator_reputation": 1838,
					"Question_score": 4,
					"Answer_content": "Another answer for discrete as opposed to continuous variables, e.g., integers versus reals, is the Kendall rank correlation. In contrast to the Spearman rank correlation, the Kendall correlation is not affected by how far from each other ranks are but only by whether the ranks between observations are equal or not.The Kendall τ coefficient is defined as:The Kendall rank coefficient is often used as a test statistic in a statistical hypothesis test to establish whether two variables may be regarded as statistically dependent. This test is non-parametric, as it does not rely on any assumptions on the distributions of  or  or the distribution of .The treatment of ties for the Kendall correlation is, however, problematic as indicated by the existence of no less than 3 methods of dealing with ties. A tie for a pair {(xi,&nbsp;yi), (xj,&nbsp;yj)} is when  xi = xj or yi = yj; a tied pair is neither concordant nor discordant.",
					"Display_name": "Carl",
					"Creater_id": 99274,
					"Start_date": "2016-11-15 12:31:45",
					"Question_id": 245931
				}, {
					"_id": "5838b73d10c7c46ef6a7f076",
					"Last_activity": "2016-11-14 15:01:37",
					"Creator_reputation": 76000,
					"Question_score": 14,
					"Answer_content": "I think you want a rank correlation.  Those are generally more robust to outliers, although it's worth recognizing that they are measuring the monotonic association, not the straight line association.  The most commonly known rank correlation is Spearman's correlation.  It is just Pearson's product moment correlation of the ranks of the data.  I wouldn't go down the path you're taking with getting the differences of each datum from the median.  The median of the distribution of X can be an entirely different point from the median of the distribution of Y, for example.  That strikes me as likely to cause instability in the calculation.  ",
					"Display_name": "gung",
					"Creater_id": 7290,
					"Start_date": "2016-11-14 14:54:53",
					"Question_id": 245931
				}



			],
			//list of topics
			"topics": ["hypothesis-testing", "anova", "multiple-regression"

			]
		}

	]
}
```
