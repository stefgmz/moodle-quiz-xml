import copy
import numbers
import lxml.etree as ET


class QConstants:
    TEMPLATE_FILE = 'quiz_num_question.xml'
    QUESTION_TAG = 'question'
    CATEGORY_TAG = 'category'
    CATEGORY_BASE = '$course$/top/'
    TEXT_TAG = 'text'
    QNAME_TAG = 'name'
    QTEXT_TAG = 'questiontext'
    ANSWER_TAG = 'answer'
    TOLERANCE_TAG = 'tolerance'
    IMG_TAG = ('<img src="@@PLUGINFILE@@/%s.png" alt="" '
               'role="presentation" '
               'class="img-responsive atto_image_button_text-bottom" '
               'width="%d" '
               'height="%d">')
    FILE_TAG = ('<file name="%s.png" path="/" '
                'encoding="base64">%s</file>')
    CDATA = '<p dir="ltr" style="text-align: left;"><p>%s</p>%s</p>'


class QSeries:
    """Creates a series of numerical questions for a moodle quiz.
    
    Creates a series of numerical questions which can be imported into
    moodle as Moodle-XML. The class takes the template file which
    contains a single question and the basic structure of Moodle-XML
    files. Each new question will be appended as a new node.
    This class allows to generate multiple similar questions by
    looping through some values.

    Attributes:
        category: A string with the name of the subcategory. If empty,
            then the questions will be added to the top level.  Use '/'
            for sub-subcategories.
    """
    
    def __init__(self, category=''):
        """Instantiates QSeries with the given category."""
        self._root = ET.parse(QConstants.TEMPLATE_FILE).getroot()
        root_iter = self._root.iterfind(QConstants.QUESTION_TAG)
        next(root_iter)
        self._question_template = next(root_iter)
        self._root.remove(self._question_template)
        self._category = category

    def add_num_question(self,
                         title,
                         question_text,
                         answer,
                         image='',
                         image_name='',
                         image_width=279,
                         image_height=486,
                         tolerance=0):
        """Appends a question to the series of questions.
        
        Args:
            title: The title of the question.
            question_text: The question itself.
            answer: The numerical answer.
            tolerance: A relative tolerance which accepts answers the deviate
                from the correct answer.
                
        Raises:
            TypeError: If the given tolerance is not a float or if the
                given answer is not a numerical value.
            ValueError: If the given tolerance is not a relative value, ie
                between 0 and 1.
        """
        new_question = copy.deepcopy(self._question_template)
        new_question.find(QConstants.QNAME_TAG).find(
            QConstants.TEXT_TAG).text = title
        questiontext_tag = new_question.find(QConstants.QTEXT_TAG)
        q_text_tag = questiontext_tag.find(QConstants.TEXT_TAG)
        q_text_tag.text = ''

        if image is not '' and image_name is not '':
            img_attrib = {
                'src': '@@PLUGINFILE@@/%s.png'%image_name,
                'role': 'presentation',
                'class': 'img-responsive atto_image_button_text-bottom',
                'width': str(image_width),
                'height': str(image_height),
            }
            img_tag = ET.Element('img', attrib=img_attrib)
            q_text_tag.text = ET.CDATA(
                QConstants.CDATA%(question_text,
                                  ET.tostring(img_tag, encoding='unicode')))
            file_attrib = {
                'name': '%s.png'%image_name,
                'path': '/',
                'encoding': 'base64',
            }
            file_tag = ET.SubElement(questiontext_tag, 'file',
                                     attrib=file_attrib)
            file_tag.text = image
        else:
            ET.SubElement(q_text_tag, 'p').text = question_text


        try:
            float(answer)
            answer_tag = new_question.find(QConstants.ANSWER_TAG)
            answer_tag.find(QConstants.TEXT_TAG).text = str(answer)
        except:
            raise TypeError('The given answer is not numeric.')
        
        try:
            float(tolerance)
        except:
            raise TypeError('The given tolerance is not a float.')
        if 0 <= tolerance < 1:
            answer_tag.find(QConstants.TOLERANCE_TAG).text = str(tolerance)
        else:
            raise ValueError('The tolerance has to be relative with respect '
                             'to the answer.')

        self._root.append(new_question)   
        
    def dump(self):
        """"Writes the whole question series to sys.stdout."""
        ET.dump(self._root)
        
    def write(self, file):
        """"Writes the whole question series to a file.
        
        Attributes:
            file: A file name or a file object opened for writing.
        """
        tree = ET.ElementTree(self._root)
        tree.write(file)
    
    @property
    def category(self):
        """Category of the question series."""
        first_slash = self._category.find('/')
        return self._category[first_slash+1:]
    
    @category.setter
    def category(self, category):
        branch = re.sub(r'^/', '', category)
        self._root.find(QConstants.QUESTION_TAG).find(
            QConstants.CATEGORY_TAG).find(
                QConstants.TEXT_TAG).text = QConstants.CATEGORY_BASE + category
