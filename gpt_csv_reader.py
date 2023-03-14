import os
import openai
import csv


openai.api_key = os.environ.get('openai_api_key')


class CSVReader:
    __prompt = '''subject: estimate 10 reviews by their happiness level from 1 to 10,
    output format: no numeration, email - happiness level, higher estimation goes first
    '''

    def __init__(self, path: str):
        self.__path: str = path
        self.__data_from_file: list[dict, ...] = []
        self.__api_response = None

    def set_prompt(self, prompt: str) -> None:
        """
        Sets the request prompt.
        :param prompt: Request prompt.
        """
        self.__prompt = prompt

    def make_estimation(self) -> None:
        """
        Main interface.
        """
        self.__read_review_file()
        self.__call_openai()
        self.__format_data()
        self.__write_review_file()

    def __read_review_file(self) -> None:
        """
        Reads a csv file to a dict.
        """
        try:
            with open(f'{self.__path}', 'r') as file:
                self.__data_from_file = list(csv.DictReader(file))

                if not self.__data_from_file:
                    print('File is empty.')
        except FileNotFoundError as e:
            print(e.args[1])

    def __call_openai(self) -> None:
        """
        Makes a request to API.
        """
        if not self.__data_from_file:
            raise Exception('No data to send')
        data_to_ai = str([[data['email'], data['review text']] for data in self.__data_from_file])
        prompt = self.__prompt + data_to_ai

        self.__api_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

    def __format_data(self) -> None:
        """
        Parses and sort the results.
        """
        content = self.__api_response.choices[0].message['content'].replace('- ', '').strip().split('\n')
        estimation = {}

        for line in content:
            key, value = line.split()
            estimation[key] = int(value)
        [print(e, e1) for e, e1 in estimation.items()]
        for data_line in self.__data_from_file:
            data_line['rate'] = estimation.get(data_line['email'], 0)

        self.__data_from_file.sort(key=lambda x: -x['rate'])

    def __write_review_file(self) -> None:
        """
        Prints to a file to the same directory.
        """
        write_file_path = self.__path[:-4] + '_analyzed.csv'
        headers = list(self.__data_from_file[0].keys())

        print(self.__api_response)
        with open(rf'{write_file_path}', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for line in self.__data_from_file:
                writer.writerow(list(line.values()))

    @property
    def prompt(self):
        return self.__prompt

    @prompt.setter
    def prompt(self, value):
        self.__prompt = value


if __name__ == '__main__':
    csv_reader = CSVReader(input('Enter location of a file: '))
    csv_reader.make_estimation()
