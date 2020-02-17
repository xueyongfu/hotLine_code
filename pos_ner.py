
import sys, os
from pyltp import Segmentor, Postagger, Parser ,SementicRoleLabeller,NamedEntityRecognizer


class nlpLtp:
    
    MODELDIR = '/home/xyf/models/ltp_model'

    #系统切词
    segmentor = Segmentor()
    segmentor.load(os.path.join(MODELDIR, "cws.model"))

    postagger = Postagger()
    postagger.load(os.path.join(MODELDIR, "pos.model"))

    namedentityrecognizer = NamedEntityRecognizer()
    namedentityrecognizer.load(os.path.join(MODELDIR, "ner.model"))

    parser = Parser()
    parser.load(os.path.join(MODELDIR, "parser.model"))

    labeller = SementicRoleLabeller()
    labeller.load(os.path.join(MODELDIR, "pisrl.model"))

    parse_dict =  {"SBV":"主谓关系", "VOB":"动宾关系", "IOB":"间宾关系", "FOB":"前置宾语", "DBL":"兼语",
                        "ATT":"定中关系", "ADV":"状中关系", "CMP":"动补关系", "POB":"介宾关系", "LAD":"左附加关系",
                        "RAD":"右附加关系", "IS":"独立结构","COO":"并列关系", "HED":"核心关系", "WP":"标点"}

    @classmethod
    def sent_segment(cls, sentence):
        words_ltp = cls.segmentor.segment(sentence)
        words_list = [w for w in words_ltp]
        return words_list

    @classmethod
    def sent_pos(cls, sentence):
        words = cls.segmentor.segment(sentence)
        postags = cls.postagger.postag(words)
        return postags

    @classmethod
    def sent_ner(cls, sentence):
        words = cls.segmentor.segment(sentence)
        postags = cls.postagger.postag(words)
        netags = cls.namedentityrecognizer.recognize(words, postags)
        return netags

    @classmethod
    def sent_syntax(cls, sentence):
        words = cls.segmentor.segment(sentence)
        postags = cls.postagger.postag(words)
        parsing = cls.parser.parse(words, postags)
        syntax = "  ".join("%d:%s" % (pars.head, pars.relation) for pars in parsing)
        return parsing, syntax

    @classmethod
    def sent_syntax_self(cls,sentence):
        print ('原文本：' + sentence)
        words = cls.sent_segment(sentence)
        print('分词结果：' + str(words))
        postags = cls.sent_pos(sentence)
        print('词性标注结果：' + str([a for a in postags]))
        parsing = cls.parser.parse(words, postags)
        parsing_a = "  ".join("%d:%s" % (pars.head, pars.relation) for pars in parsing)
        print('句法分析结果：' + parsing_a)

        parsing_b = zip(words, parsing)
        for par in parsing_b:
            if par[1].relation in ['WP', 'HED']:
                print('"'+par[0]+'"是'+cls.parse_dict[par[1].relation], end=',  ')
            else:
                print('"'+par[0]+'"'+'与'+'"'+words[par[1].head-1]+'"'+'：'+cls.parse_dict[par[1].relation], end=',  ')

    @classmethod
    def sent_role(cls, sentence):
        words = cls.sent_segment(sentence)
        postags = cls.sent_pos(sentence)
        parsing = cls.parser.parse(words, postags)

        roles = cls.labeller.label(words, postags, parsing)
        for role in roles:  #roles是谓词
            print(role.index, "".join(
                ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
            
            for arg in role.arguments:
                if arg.name == 'A1':
                    words_list=words[arg.range.start:arg.range.end+1]
                    print(''.join(words_list))


def get_pos_ner(sentence):
    tokens = nlpLtp.sent_segment(sentence)
    pos = nlpLtp.sent_pos(sentence)
    ner = nlpLtp.sent_ner(sentence)
    return {'segment':tokens, 'pos':list(pos), 'ner':list(ner)}
    

if __name__ == '__main__':
    print(get_pos_ner('今天天气好'))










