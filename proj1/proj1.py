import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth',100)
pd.set_option('display.width',1000)


def print_dataframe(dataframe, print_column=True, print_rows=True):
    if print_column:
        print(",".join([column for column in dataframe]))
    if print_rows:
        for index, row in dataframe.iterrows():
            print(",".join([str(row[column]) for column in dataframe]))


def merged():
    summer = 'Olympics_dataset1.csv'
    winter = 'Olympics_dataset2.csv'

    df1 = pd.read_csv(summer, skiprows = 1, thousands = ',')
    df2 = pd.read_csv(winter, skiprows = 1, thousands = ',')
    df3 = pd.merge(df1, df2, on ='Unnamed: 0')

    df3.rename(columns = {'Unnamed: 0': 'Country', 'Total.1': 'Total_Medals'}, inplace = True)
    df3.apply(pd.to_numeric, errors = 'ignore')
    df3.astype(int, errors = 'ignore')

    return df3


'''
Question 1: 
Merge the two datasets Olympics_dataset1.csv and Olympics_dataset2.csv and display the first five rows (do not concatenate the datasets). 
'''


def question_1():
    df = merged()
    answer = df.head(5)

    return answer


'''
Question 2: 
Set the index as the country name and then display the first country in the Dataframe. 
'''


def question_2():
    df = merged()
    df = df.set_index(['Country'])
    answer = df.head(1)

    return answer


'''
Question 3: 
Remove the rubish column and display the first five rows.
'''


def question_3():
    df = merged()
    df = df.drop(columns =['Rubish'])
    answer = df.head(5)

    return answer


'''
Question 4: 
Remove the rows with NaN fields and display the last ten rows.
'''


def question_4():
    df = merged()
    df = df.dropna(how = 'any')
    answer = df.tail(10)

    return answer


'''
Question 5: 
Calculate and display which country has won the most gold medals in summer games? 
'''


def question_5():
    df = merged()
    df = df.dropna(how = 'any')
    df = df.drop(df.index[-1])
    index = df['Gold_x'].idxmax
    answer = df.loc[index]

    return answer.Country, answer.Gold_x


'''
Question 6: 
Calculate and display which country had the biggest difference between their summer and winter gold medal? 
'''


def question_6():
    df = merged()
    df = df.dropna(how = 'any')
    df = df.drop(df.index[-1])

    df['Gold_Difference'] = abs(df.Gold_x - df.Gold_y)

    index = df['Gold_Difference'].idxmax()
    answer = df.loc[index]

    return answer.Country, answer.Gold_Difference


'''
Question 7: 
Sort the countries in descending order, according to the number of total of medals earned throughout the history 
and display the first and last 5 rows. 
'''


def question_7():
    df = merged()
    df = df.dropna(how = 'any')
    df = df.drop(df.index[-1])
    df = df.sort_values('Total_Medals', ascending = False)

    #return df.head(5), df.tail(5)
    return df


'''
Question 8: 
Plot a bar chart of the top 10 countries (according to the sorting in Question 7). 
For each country use a stacked bar chart showing for each county the total medals for winter and summer games. 
'''


def question_8():
    df = merged()
    df = df.dropna(how = 'any')
    df = df.drop(df.index[-1])
    df = df.sort_values('Total_Medals', ascending = False)
    df = df.head(10)
    N = 10
    summer = df.Total_x
    winter = df.Total_y
    ind = np.arange(N)
    height = 0.5
    p1 = plt.barh(ind, winter + summer, height)
    p2 = plt.barh(ind, summer, height)
    plt.xlabel('Scores')
    plt.title('Medals for Winter and Summer Games')
    plt.yticks(ind, df.Country)
    plt.legend((p1[0], p2[0]), ('Winter Games', 'Summer Games'))
    plt.show()

    return


'''
Plot a bar chart of the countries (United States, Australia, Great Britain, Japan, New Zealand). 
For each county you need to show the gold, silver and bronze medals for winter games. See example below of the chart: 
'''


def question_9():
    df = merged()
    df = df.set_index(['Country'])
    usa = df.loc[' United States (USA) [P] [Q] [R] [Z]']
    aus = df.loc[' Australia (AUS) [AUS] [Z]']
    gbr = df.loc[' Great Britain (GBR) [GBR] [Z]']
    jpn = df.loc[' Japan (JPN)']
    nzl = df.loc[' New Zealand (NZL) [NZL]']

    n_groups = 5
    golds = (usa.Gold_y, aus.Gold_y, gbr.Gold_y, jpn.Gold_y, nzl.Gold_y)
    slivers = (usa.Silver_y, aus.Silver_y, gbr.Silver_y, jpn.Silver_y, nzl.Silver_y)
    bronzes = (usa.Bronze_y, aus.Bronze_y, gbr.Bronze_y, jpn.Bronze_y, nzl.Bronze_y)

    index = np.arange(n_groups)
    bar_width = 0.2

    plt.bar(index, golds, bar_width, label = 'Gold Medals')

    plt.bar(index + bar_width, slivers, bar_width, label = 'Silver Medals')

    plt.bar(index + bar_width + bar_width, bronzes, bar_width, label = 'Bronze Medals')

    plt.title('Winter Games')
    plt.xticks(index + bar_width / 3, ('United States', 'Australia', 'Great Britain', 'Japan', 'New Zealand'))
    plt.legend()
    plt.show()

    return


if __name__ == '__main__':

    print('Question 1 is showing as below: \n')
    #print(question_1(), '\n')
    print_dataframe(question_1(),'\n')
    print('Question 2 is showing as below: \n')
    #print(question_2(), '\n')
    print_dataframe(question_2(), '\n')
    print('Question 3 is showing as below: \n')
    #print(question_3(), '\n')
    print_dataframe(question_3(), '\n')
    print('Question 4 is showing as below: \n')
    #print(question_4(), '\n')
    print_dataframe(question_4(), '\n')
    print('Question 5 is showing as below: \n')
    answer_5 = question_5()
    print('{} has won the most gold medals in summer games, the number is {}. \n'.format(answer_5[0][1:13],answer_5[1]))
    print('Question 6 is showing as below: \n')
    answer_6 = question_6()
    print('{} had the biggest difference between their summer and winter gold medal, the number is {}. \n'.format(answer_6[0][1:13],answer_6[1]))
    print('Question 7 is showing as below: \n')
    #print(question_7().head(5), '\n')
    #print(question_7().tail(5), '\n')
    print_dataframe(question_7().head(5), '\n')
    print_dataframe(question_7().tail(5), '\n')
    print('Question 8 is showing as below: \n')
    question_8()
    print('Question 9 is showing as below: \n')
    question_9()