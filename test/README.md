Внутри папки находится набор скриптов для проверки стиля исходников.

Для запуска проверки необходимо:

* Установить [pep8](http://pep8.readthedocs.org/en/latest/intro.html)
* В той же директории, где находится LearningEnglish, создать пустую папку "reports"
* Находясь в директории LearningEnglish выполнить команду:
    ```cmd
test\windows_check_syntax.bat "path_to_python"
    ```
где:  
    * path_to_python - путь к директории с python  

    Например:
    ```cmd
test\windows_check_syntax.bat "c:\Soft\Python26"
    ```

    После этого в директории "reports" создастся файл pep8.out со списоком ошибок оформления, если они есть конечно.

Для частичного автоматического исправления нужно:

* Установить [autopep8](https://github.com/hhatto/autopep8)
* Находясь в директории LearningEnglish выполнить команду:
    ```cmd
test\windows_fix_syntax.bat "path_to_python" "path_to_file"
    ```
где:  
    * path_to_python - путь к директории с python  
    * path_to_file - путь к файлу, который нужно исправить

    Например:
    ```cmd
test\windows_fix_syntax.bat "c:\Soft\Python26" "src\statistic.py"
    ```

    После этого, autopep8 по возможности поправит все ошибки оформления согласно стандарту pep8. Однако результаты лучше проверить вручную.