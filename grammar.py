

class Word:
    '''根据lexicon的定义，每一个Word由它的text和lexical_list组成
    如‘老’的text就是'老'，它的lexical_list为['ADJ','ADV']'''
    def __init__(self, text: str, lexical_list: list):
        self.text = text
        self.lexical_list = lexical_list

    def __str__(self):
        return f"{self.text} : {' '.join(self.lexical_list)}"

class Rule:
    '''Rule表示规则，每个Rule实例有不同的id（这样可以在将rule对应的arc加入chart时进行区分，避免多次加入）
    left和right就如字面意思表示rule的左右两段内容，如S->NP VP，left = 'S', right = ['NP', 'VP'] '''
    count = 0

    def __init__(self, left: str, right: list):
        Rule.count += 1
        self.rule_id = Rule.count
        self.left = left
        self.right = right

    def __str__(self):
        return f"{self.left} -> {' '.join(self.right)}"


class Arc:
    '''Arc代表chart中的active arc，其属性含义分别为：
    rule: 产生arc所使用的rule
    start: arc开始的position
    end: arc结束的position（按照列表惯例，不包含）
    current: arc所使用的rule右侧匹配的位置，如S->NP * VP，则current = 1'''
    def __init__(self, rule: Rule, start: int, end: int, current: int):
        self.rule = rule
        self.start = start
        self.end = end
        self.current = current

    def __str__(self):
        return f"{self.rule.left} -> {' '.join(self.rule.right[:self.current])} * {' '.join(self.rule.right[self.current:])}"

class Constituent:
    '''Constituent代表句子中的一个subpart，其属性含义分别为
  	constituent_id: 用来区分不同的Constituent
  	type: Constituent的类型，如NP
  	start：Constituent的开始position
  	end: Constituent结束的position（不包含）
  	rule：得到Constituent的rule'''
    count = 0

    def __init__(self, type: str, start: int, end: int, rule=None):
        Constituent.count += 1
        self.constituent_id = Constituent.count
        self.type = type
        self.start = start
        self.end = end
        self.rule = rule

def add_to_chart(arc: Arc, chart: list):
    '''将一个arc加入到chart中'''
    
    # 检验当前chart中是否已经包含了这个arc，如果没有，才将其加入。
    for item in chart:
        if item.rule.rule_id != arc.rule.rule_id:
            continue
        if item.start != arc.start:
            continue
        if item.end != arc.end:
            continue
        if item.current != arc.current:
            continue
        return
    chart.append(arc)  

def bottom_up_parsing(words: list, rules: list):
    '''bottom up parsing algorithm
	args:
		words: list of Word
		rules: list of Rule
	return:
		agenda_backup: list of constituent, 按顺序保存了所有搜索到的constituent
		chart: list of Arc, 按顺序保存了所有加入到chart的arc
		'''
    
    now = 0	# 表示当前position
    agenda = []
    agenda_backup = []
    chart = []
	
    # 若words或agenda不为空
    while now < len(words) or agenda:
        # 如果agenda为空
        if not agenda:
            # 将next word的所有inptretation加入agenda
            word = words[now]
            for lexical in word.lexical_list:
                agenda.append(Constituent(lexical, now, now+1))
            now += 1
        # 从agenda中取出一个constituent
        constituent = agenda.pop()
        # 将constituent备份，之后会return
        agenda_backup.append(constituent)
		
        ## 首先要根据rule新加active arc，然后要根据chart中已有的active arc进行扩展
        
        # 对于每一个rule
        for rule in rules:
            # 如果rule右侧第一个constituent与当前constituent相同，且rule右侧只有一个constituent
            if rule.right[0] == constituent.type and len(rule.right) == 1:
                # 那么，rule左侧的constituent解析完毕，将其加入agenda
                agenda.append(Constituent(rule.left, constituent.start, constituent.end, rule))
            # 如果rule右侧第一个constituent与当前constituent相同，但rule右侧不止一个constituent
            elif rule.right[0] == constituent.type and len(rule.right) > 1:
                # 那么，出现了新的active arc，将其加入chart
                arc = Arc(rule, constituent.start, constituent.end, 1)
                add_to_chart(arc, chart)
        # arc extension algorithm: 对于chart中每一个arc
        for arc in chart:
            # 如果arc的end不等于当前constituent的start，查看下一个arc
            if arc.end != constituent.start:
                continue
            # 如果当前constituent的type与arc对应的rule的下一个constituent相同且这个constituent不是rule的最后一个，则新加一条active arc
            if constituent.type == arc.rule.right[arc.current] and arc.current + 1 != len(arc.rule.right):
                add_to_chart(Arc(arc.rule, arc.start, constituent.end, arc.current+1), chart)
            # 如果当前constituent的type与arc对应的rule的下一个constituent相同且这个constituent是rule的最后一个（说明当前arc解析完毕），将新产生的constituent（即rule左侧的constituent）加入agenda
            elif constituent.type == arc.rule.right[arc.current] and arc.current + 1 == len(arc.rule.right):
                agenda.append(Constituent(arc.rule.left, arc.start, constituent.end, arc.rule))
  
    return agenda_backup, words, chart 

def arc_introduction_algorithm(arc: Arc, chart: list, rules: list):
    '''arc introduction algorithm: 参照书上伪代码'''
    
    # 首先将当前arc加入chart
    for item in chart:
        if item.rule.rule_id != arc.rule.rule_id:
            continue
        if item.start != arc.start:
            continue
        if item.end != arc.end:
            continue
        if item.current != arc.current:
            continue
        return 
    chart.append(arc)
	
    # 对于每一个rule.left等于arc.rule.right[arc.current]的规则，产生一条arc并调用arc introduction algorithm
    for rule in rules:
        if rule.left == arc.rule.right[arc.current]:
            arc_introduction_algorithm(Arc(rule, arc.end, arc.end, 0), chart, rules)

def top_down_parsing(words: list, rules: list):
    '''bottom up parsing algorithm
	args:
		words: list of Word
		rules: list of Rule
	return:
		agenda_backup: list of constituent, 按顺序保存了所有搜索到的constituent
		words: list of words, 与传入的words相同
		chart: list of Arc, 按顺序保存了所有加入到chart的arc
		'''
    now = 0
    agenda = []
    agenda_backup = []
    chart = []

    # 首先根据左侧为S的rule，建立新的active arc并调用arc_introduction_algorithm
    for rule in rules:
        if rule.left == 'S':
            arc_introduction_algorithm(Arc(rule, 0, 0, 0), chart, rules)
	
    # 一下大部分与bottom_up_parsing一样，不再给出注释。
    
    while now < len(words) or agenda:
        if not agenda:
            word = words[now]
            for lexical in word.lexical_list:
                agenda.append(Constituent(lexical, now, now+1))
            now += 1
        constituent = agenda.pop()
        agenda_backup.append(constituent)
        for arc in chart:
            if arc.end != constituent.start:
                continue

            if arc.rule.right[arc.current] == constituent.type and arc.current + 1 == len(arc.rule.right):
                agenda.append(Constituent(arc.rule.left, arc.start, constituent.end, arc.rule))
            elif arc.rule.right[arc.current] == constituent.type and arc.current + 1 < len(arc.rule.right):
                # 与bottom_up_parsing不同，此处调用arc_introduction_algorithm来加入新的active arc
                arc_introduction_algorithm(Arc(arc.rule, arc.start, constituent.end, arc.current + 1), chart, rules)
    return agenda_backup, words, chart


def output(constituent_list:list, words:list, arc_list:list):
    '''每个word输出宽度为20
        对于长度为0的arc，没有*占位符'''
    for constituent in reversed(constituent_list):
        prefix = constituent.start * 20
        length = constituent.end * 20 - prefix
        print(' '*prefix + f'{constituent.type:*<{length}}')

    print(''.join([f'{word.text:*<19}' for word in words]))

    for arc in arc_list:
        prefix = arc.start * 20
        length = arc.end * 20 - prefix
        print(' '*prefix + f'{str(arc):*<{length}}')

    print('size of constituent_list: ', len(constituent_list))
    print('size of arc_list: ', len(arc_list))

lexicon = {
    "老":['ADJ', 'ADV'],
    "谢": ['SURNAME', 'V'],
    "在": ['V','ADV','PREP'],
    "编辑": ['N','V'],
    '学习': ['N','V'],
    '手册': ['N']
}

grammar = [
    ['S',['NP','VP']],
    ['NP',['N']],
    ['NP',['ADJ','SURNAME']],
    ['NP',['N','N']],
    ['NP',['V','N']],
    ['NP',['ADJ','N']],
    ['PP',['PREP','NP']],
    ['VP',['V']],
    ['VP',['V','NP']],
    ['VP',['ADV','VP']],
    ['VP',['PP','VP']],
]

words = []
for key, item in lexicon.items():
    words.append(Word(key, item))

rules = []
for left, right in grammar:
    rules.append(Rule(left, right))

print('bottom_up_parsing: ')
output(*bottom_up_parsing(words, rules))

print('top_down_parsing: ')
output(*top_down_parsing(words, rules))