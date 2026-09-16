# Dados do experimento Nav2

Esta pasta contém as entradas utilizadas para reproduzir o experimento com Behavior Trees reais do Nav2.

## Behavior Trees analisadas

- `follow_point.xml`
- `navigate_to_pose_w_bounds_check.xml`
- `navigate_to_pose_w_replanning_and_recovery.xml`
- `navigate_through_poses_w_replanning_and_recovery.xml`
- `navigate_on_route_graph_w_recovery.xml`

Esses arquivos foram obtidos do repositório oficial `ros-navigation/navigation2`, no diretório `nav2_bt_navigator/behavior_trees/`.

O commit ou tag exato da coleta original não foi registrado durante o experimento. Por esse motivo, o repositório preserva as cópias exatas dos XMLs efetivamente utilizados e não atribui retroativamente um SHA de origem.

## `nav2_tree_nodes.xml`

O experimento original utilizou o arquivo oficial completo `nav2_tree_nodes.xml` para obter as portas de entrada disponíveis de cada tipo de nó.

Para tornar este repositório mais compacto e manter apenas os dados efetivamente consumidos pelo extrator, o arquivo aqui incluído é um **subconjunto de reprodução**. Ele preserva, para todos os tipos de nós presentes nas cinco BTs, os IDs e nomes das `input_port` utilizados pelo cálculo de parametrização e adaptabilidade.

Foi feita uma validação comparando a execução com o arquivo oficial completo e com este subconjunto. O CSV final produzido para as cinco BTs foi numericamente idêntico.

Consulte [`../../docs/experimento_nav2.md`](../../docs/experimento_nav2.md) para a descrição completa das regras de extração.
