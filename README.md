### Шахматная игра с консольным и графическим интервейсом.(python 3.7)


_Пример запуска графического интерфейса_: `python gui.py`

_Примеры запуска консольного интерфейса_:
 
+ `python cui.py`
+ `python cui.py --mode H-H`
+ `python cui.py --endless`
+ `python cui.py --load fileName`
+ `python cui.py --painter`

## Реализованные правила：
+ Шах/мат/пат
+ Взятие на проходе
+ Рокировка
+ Превращение пешки
+ Ничья (позиция повторилась трижды подряд; либо совершено 85 ходов [с возможностью отключения опцией запуска])

## Дополнительные возможности:
+ Ведение лога партии, undo/redo
+ Режимы игры: H-H, H-AI, AI-H, AI-AI
+ Возможность сохранить и загрузить игру
+ Если H играет чёрными, доска автоматически поворачивается

#### Доп.фигура [включается опцией]:
+ ход: через 1 поле(в любом направлении), затем на 1 (по вертикали или горизонтали)
+ не рубит фигуры
+ может фигуру перепрыгнуть на первом этапе хода, перекрасив её в другой цвет, при этом она сама окрашивается в противоположный и этой фигурой нельзя ходить 2 хода
+ фигура есть у обоих игроков, расположена на 3 линии справа
+ ход происходит в два этапа, например:
    
    `from: h6`
    
    `to: h5`
    
    `from: h5`
    
    `to: h6`
