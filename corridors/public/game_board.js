/*
    I want a mechanism for highlighting legal moves.
    
    This means 2 things: SENDING the legal moves with the board state.
    Painting them in response to mouse activity.
*/
Ractive.components.GameBoard = Ractive.extend({
    css:`
    
    .cm-chessboard .board.input-enabled .square {
  cursor: pointer; }

.cm-chessboard .board .border {
  fill: rgba(0, 0, 0, 0.7); }

.cm-chessboard .board .square.white {
  fill: #eedab6; }

.cm-chessboard .board .square.black {
  fill: #c7a47b; }

.cm-chessboard.has-border .board .border {
  fill: #eedab6; }

.cm-chessboard.has-border .board .border-inner {
  fill: #c7a47b; }

.cm-chessboard .coordinates {
  pointer-events: none;
  user-select: none; }
  .cm-chessboard .coordinates .coordinate {
    fill: rgba(0, 0, 0, 0.7);
    font-size: 7px;
    cursor: default; }



    `,    
    template:`
        <svg width="550" height="490" class="cm-chessboard default">
            <g class="board input-enabled">
                <rect width="550" height="490" class="border"></rect>
                <g transform="translate(50,20) ">
                    {{#each [0,1,2,3,4,5,6,7,8] as j}}
                        {{#each [0,1,2,3,4,5,6,7,8] as i}}
                            <rect 
                                x="{{5+(i*50)}}" 
                                y="{{5+(j*50)}}" 
                                rx="3"
                                ry="3"
                                width="40" 
                                height="40" 
                                class="square black"
                                >
                             </rect>
                        {{/each}}
                    {{/each}}
                    <g class="piece blue" transform="translate({{50*game.board.pieces.blue.location[1]}},{{50*game.board.pieces.blue.location[0]}})">
                        <circle cx="25" cy="25" r="15" stroke="black" stroke-width="1" fill="blue" />
                    </g>
                    <g class="piece red" transform="translate({{50*game.board.pieces.red.location[1]}},{{50*game.board.pieces.red.location[0]}})">
                        <circle cx="25" cy="25" r="15" stroke="black" stroke-width="1" fill="red" />
                    </g>
                    <g transform="translate(50,50)">
                        {{#each game.board.walls as row:j}}
                            {{#each row as wall:i}}
                                {{#if wall==1}}
                                    <g transform="translate({{i*50}},{{j*50}})">
                                        <rect x="-45" y="-3" width="90" height="6" stroke="black" rx="2" ry="2">
                                        </rect>
                                    </g>
                                {{/if}}
                                {{#if wall==-1}}
                                    <g transform="translate({{i*50}},{{j*50}})">
                                        <rect x="-3" y="-45" width="6" height="90" stroke="black" rx="2" ry="2">
                                        </rect>
                                    </g>
                                {{/if}}
                            {{/each}}
                        {{/each}}
                    </g>
                </g>
            </g>
        </svg>
        <input class='input' type="text" value='{{new_command}}' on-keyup="@this.keyup(@event.code, ws,new_command)" placeholder="command"/>
        
        
    `,
    keyup(code,ws,new_command){
        if (code!='Enter')
            return;
        ws.send('game.command',new_command);
        this.set('new_command','')
    }
});