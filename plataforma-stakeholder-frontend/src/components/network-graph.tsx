import {
  CSSProperties,
  FC,
  useCallback,
  useMemo,
  useState,
  useRef,
  useEffect,
} from 'react'

import {
  SigmaContainer,
  useLoadGraph,
  useRegisterEvents,
  useSigma,
  ControlsContainer,
  ZoomControl,
  FullScreenControl,
} from '@react-sigma/core'
import '@react-sigma/core/lib/style.css'

import { NodeImageProgram } from '@sigma/node-image'

import Graph from 'graphology'
import louvain from 'graphology-communities-louvain'

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'

import { Loader2, X } from 'lucide-react'

import { useQuery } from '@tanstack/react-query'
import { getLawyers } from '@/http/lawyers/get-lawyers'
import { getOffices } from '@/http/offices/get-offices'
import { getEmpresas } from '@/http/empresa/get-empresas'
import { getPessoas } from '@/http/pessoa/get-pessoas'
import { Separator } from './ui/separator'
import { formatCpfCnpj } from '@/utils/format-cpf-cnpj'

import ForceGraph2D from 'react-force-graph-2d'

import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Settings, ChevronsRight, ChevronsLeft } from 'lucide-react'
import Link from 'next/link'

type Links = {
  source: string
  target: string
  label: string
}

type Nodes = {
  id: string
  subgroup: string
  title: string
  label: string
  type: string
  documento: string
  em_prospeccao: boolean
  matched: boolean
  root: boolean
  stakeholder: boolean
}

type NetworkGraphProps = {
  clusters: {
    links: Links[]
    nodes: Nodes[]
  }[]
}

export const NetworkGraph: FC<
  NetworkGraphProps & { style?: CSSProperties }
> = ({ clusters, style }) => {
  console.log('NetworkGraph component rendering (using react-force-graph)');

  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [selectedNodeData, setSelectedNodeData] = useState<Nodes | null>(null);

  const [openControls, setOpenControls] = useState(true);
  const [chargeStrength, setChargeStrength] = useState(-30);
  const [linkStrength, setLinkStrength] = useState(1.0);
  const [linkDistance, setLinkDistance] = useState(30);
  const [centerStrength, setCenterStrength] = useState(0.2);
  const [forceXStrength, setForceXStrength] = useState(0.1);
  const [forceYStrength, setForceYStrength] = useState(0.1);
  const [collideRadius, setCollideRadius] = useState(8);
  const [alphaDecay, setAlphaDecay] = useState(0.01);
  const [velocityDecay, setVelocityDecay] = useState(0.4);
  const [distanceMax, setDistanceMax] = useState(200);

  const { data: queryData, isLoading: isQueryLoading } = useQuery<any>({
    queryKey: ['node-details', selectedNodeData?.id],
    queryFn: async () => {
      if (!selectedNodeData) return null

      const id = Number(selectedNodeData.id.split(':')[1])

      switch (selectedNodeData.type) {
        case 'Advogado':
          return getLawyers({ advogado_id: id })
        case 'Escritorio':
          return getOffices({ escritorio_id: id })
        case 'Empresa':
          return getEmpresas({ empresa_id: id })
        case 'Pessoa':
          return getPessoas({ pessoa_id: id })
        default:
          return Promise.reject(new Error('Tipo desconhecido'))
      }
    },
    enabled: isSheetOpen && !!selectedNodeData,
  })

  const handleNodeClick = useCallback((node: any /* Use more specific type if available from react-force-graph */) => {
    console.log('Node clicked (react-force-graph):', node);
    const originalNode = clusters
      .flatMap((cluster) => cluster.nodes)
      .find((n) => n.id === node.id);

    if (originalNode) {
      setSelectedNodeData(originalNode);
      setIsSheetOpen(true);
    } else {
      console.warn("Original node data (type Nodes) not found for clicked node:", node.id, "Displaying data from graph node.");
      setSelectedNodeData({
        id: node.id,
        label: node.name || node.id,
        type: node.originalType || 'Desconhecido',
        subgroup: node.subgroup || '',
        title: node.name || node.id,
        documento: node.documento || '',
        em_prospeccao: node.em_prospeccao || false,
        matched: node.isMatched || false,
        root: node.val > 10,
        stakeholder: node.isStakeholder || false,
      });
      setIsSheetOpen(true);
    }
  }, [clusters]);

  const graphData = useMemo(() => {
    console.log("Transforming data for react-force-graph with Louvain...");
    const graph = new Graph({ multi: false, allowSelfLoops: false });

    const uniqueNodes = new Map<string, any>();

    const BASE_NODE_SIZE = 10;
    const ROOT_NODE_SIZE = 20;

    if (!clusters) {
      console.log("No clusters data, returning empty graph.");
      return { nodes: [], links: [] };
    }

    clusters.forEach(cluster => {
      cluster.nodes.forEach(node => {
        if (!graph.hasNode(node.id)) {
          graph.addNode(node.id, {
            id: node.id,
            name: node.label,
            val: node.root ? ROOT_NODE_SIZE : BASE_NODE_SIZE,
            color: '#9ca3af',
            originalType: node.type,
            isStakeholder: node.stakeholder,
            isMatched: node.matched,
            originalData: node,
          });
          uniqueNodes.set(node.id, graph.getNodeAttributes(node.id));
        }
      });
    });

    const processedLinkPairs = new Set<string>();
    clusters.forEach(cluster => {
      cluster.links.forEach(link => {
        const sourceExists = graph.hasNode(link.source);
        const targetExists = graph.hasNode(link.target);
        const pairKey = [link.source, link.target].sort().join('--');

        if (sourceExists && targetExists && !processedLinkPairs.has(pairKey)) {
          if (!graph.hasEdge(link.source, link.target) && !graph.hasEdge(link.target, link.source)) {
            try {
              graph.addEdge(link.source, link.target, {
                name: link.label || 'Ligação',
                color: '#cccccc',
                width: 0.5,
                originalLink: link,
              });
              processedLinkPairs.add(pairKey);
            } catch (error) {
              console.error(`Failed to add edge between ${link.source} and ${link.target}:`, error);
            }
          }
        } else if (!sourceExists || !targetExists) {
          // console.warn(`Skipping link due to missing node(s): ${link.source} -> ${link.target}`);
        }
      });
    });

    if (graph.order > 0 && graph.size > 0) {
      console.log(`Running Louvain on graph with ${graph.order} nodes and ${graph.size} edges.`);
      try {
        louvain.assign(graph);
        console.log("Louvain community detection complete.");
        const communityMap: { [key: number]: number } = {};
        graph.forEachNode((node, attrs) => {
          if (attrs.community !== undefined) {
            communityMap[attrs.community] = (communityMap[attrs.community] || 0) + 1;
          }
        });
        console.log("Community distribution:", communityMap);
      } catch (e) {
        console.error("Error running Louvain:", e);
        graph.forEachNode((node) => {
          graph.setNodeAttribute(node, 'community', 0);
        });
      }
    } else {
      console.log("Skipping Louvain: Graph is empty or has no edges.");
      graph.forEachNode((node) => {
        graph.setNodeAttribute(node, 'community', 0);
      });
    }

    const nodesArray = graph.mapNodes((nodeId, attributes) => ({
      ...attributes,
    }));
    const linksArray = graph.mapEdges((edge, attributes, source, target, sourceAttributes, targetAttributes) => ({
      ...attributes,
      source: source,
      target: target,
      sourceNode: sourceAttributes,
      targetNode: targetAttributes,
    }));

    console.log(`Data transformed: ${nodesArray.length} nodes, ${linksArray.length} links. Community info added.`);
    return { nodes: nodesArray, links: linksArray };

  }, [clusters]);

  // --- START: Image Preloading ---
  const imageCacheRef = useRef<Record<string, HTMLImageElement>>({});
  const iconUrls = useMemo(() => [
    '/icons/pessoa.png',
    '/icons/stakeholder2.png',
    '/icons/stakeholder-matched.png',
    '/icons/empresa.png',
    '/icons/socio.png',
    '/icons/advogado.png',
  ], []);

  useEffect(() => {
    console.log('Preloading icons...');
    let loadedCount = 0;
    iconUrls.forEach(url => {
      if (!imageCacheRef.current[url]) {
        const img = new Image();
        img.src = url;
        img.onload = () => {
          imageCacheRef.current[url] = img;
          loadedCount++;
          console.log(`Loaded icon: ${url}`);
          if (loadedCount === iconUrls.length) {
            console.log('All icons preloaded.');
          }
        };
        img.onerror = () => {
          console.error(`Failed to load icon: ${url}`);
          imageCacheRef.current[url] = null as any;
        };
      }
    });
  }, [iconUrls]);
  // --- END: Image Preloading ---

  const getNodeIconUrl = (node: any): string => {
    if (node.isStakeholder) {
      return '/icons/stakeholder2.png';
    }
    if (node.isMatched) {
      return '/icons/stakeholder-matched.png';
    }
    switch (node.originalType) {
      case 'Empresa':
        return '/icons/empresa.png';
      case 'Socio':
        return '/icons/socio.png';
      case 'Advogado':
        return '/icons/advogado.png';
      case 'Pessoa':
        return '/icons/pessoa.png';
      case 'Escritorio':
        return '/icons/escritorio.png';
      default:
        return '/icons/pessoa.png';
    }
  }

  // Effect para ajustar as forças D3, agora dependendo dos estados
  useEffect(() => {
    if (fgRef.current && graphData.nodes.length > 0) {
      console.log("Applying custom D3 forces based on UI controls...");
      let simulationReheated = false;
      const d3 = fgRef.current.d3; // Acessa d3 para adicionar novas forças

      // 1. Ajustar Repulsão (Charge)
      const chargeForce = fgRef.current.d3Force('charge');
      if (chargeForce) {
        chargeForce
          .strength(chargeStrength)
          .distanceMax(distanceMax);
        console.log(`Set charge strength to ${chargeStrength} and distanceMax to ${distanceMax}.`);
        simulationReheated = true;
      }

      // 2. Ajustar Links (Força e Distância UNIFICADAS)
      const linkForce = fgRef.current.d3Force('link');
      if (linkForce) {
        // Remover lógica condicional
        linkForce.strength(linkStrength); // Usar estado unificado
        linkForce.distance(linkDistance); // Usar estado unificado

        console.log(`Set link strength (${linkStrength}) and distance (${linkDistance})`);
        simulationReheated = true;
      }

      // 3. Ajustar Força de Colisão (RAIO FIXO)
      const collideForce = fgRef.current.d3Force('collide');
      if (d3) {
        if (!collideForce) {
          fgRef.current.d3Force('collide', d3.forceCollide().radius(collideRadius)); // Usar raio fixo do estado
          console.log(`Added collision force with radius ${collideRadius}.`);
        } else {
          collideForce.radius(collideRadius); // Usar raio fixo do estado
          console.log(`Adjusted collision force radius to ${collideRadius}.`);
        }
        simulationReheated = true;
      } else {
        console.warn("Could not access d3 object to configure collision force.");
      }

      // 4. Ajustar Força de Centralização
      const centerForce = fgRef.current.d3Force('center');
      if (centerForce) {
        centerForce.strength(centerStrength);
        console.log(`Adjusted center force strength to ${centerStrength}.`);
        simulationReheated = true;
      } else if (d3) {
        fgRef.current.d3Force('center', d3.forceCenter().strength(centerStrength));
        console.log(`Added center force with strength ${centerStrength}.`);
        simulationReheated = true;
      }

      // 5. Adicionar/Ajustar Força X (REMOVIDO/COMENTADO)
      /*
      const forceX = fgRef.current.d3Force('x');
      if (d3) {
        if (!forceX) {
          fgRef.current.d3Force('x', d3.forceX(0).strength(forceXStrength)); // Alvo 0, força do estado
          console.log(`Added forceX targeting center with strength ${forceXStrength}.`);
        } else {
          forceX.strength(forceXStrength); // Ajusta força do estado
          console.log(`Adjusted forceX strength to ${forceXStrength}.`);
        }
        simulationReheated = true;
      } else {
        console.warn("Could not access d3 object to configure forceX.");
      }
      */
      const currentForceX = fgRef.current.d3Force('x');
      if (currentForceX) {
        fgRef.current.d3Force('x', null); // Remove a força X se existir
        console.log("Removed forceX.");
        simulationReheated = true;
      }

      // 6. Adicionar/Ajustar Força Y (REMOVIDO/COMENTADO)
      /*
      const forceY = fgRef.current.d3Force('y');
      if (d3) {
        if (!forceY) {
          fgRef.current.d3Force('y', d3.forceY(0).strength(forceYStrength)); // Alvo 0, força do estado
          console.log(`Added forceY targeting center with strength ${forceYStrength}.`);
        } else {
          forceY.strength(forceYStrength); // Ajusta força do estado
          console.log(`Adjusted forceY strength to ${forceYStrength}.`);
        }
        simulationReheated = true;
      } else {
        console.warn("Could not access d3 object to configure forceY.");
      }
      */
      const currentForceY = fgRef.current.d3Force('y');
      if (currentForceY) {
        fgRef.current.d3Force('y', null); // Remove a força Y se existir
        console.log("Removed forceY.");
        simulationReheated = true;
      }

      // Reaquecer a simulação APENAS se alguma força foi modificada
      if (simulationReheated) {
        console.log("Reheating simulation...");
        fgRef.current.d3ReheatSimulation();
      }
    }
  }, [
    graphData,
    chargeStrength,
    linkStrength,
    linkDistance,
    centerStrength,
    collideRadius,
    distanceMax,
  ]);

  if (graphData.nodes.length === 0) {
    return <div>Carregando ou sem dados para o grafo...</div>;
  }

  const fgRef = useRef<any>();

  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh', ...style }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeId="id"
        nodeLabel="name"
        nodeVal="val"
        nodeColor="color"
        linkSource="source"
        linkTarget="target"
        linkColor={() => '#cccccc'}
        linkWidth={() => 0.5}
        linkLabel="name"
        backgroundColor="#fafafa"
        onNodeClick={handleNodeClick}
        enableNodeDrag={true}
        d3AlphaDecay={alphaDecay}
        d3VelocityDecay={velocityDecay}
        onEngineTick={() => {
          // Lógica de contenção comentada para permitir layout natural
          /*
          const nodes = graphData.nodes;
          const radius = 300;

          nodes.forEach((node: any) => {
            const nodeX = node.x ?? 0;
            const nodeY = node.y ?? 0;
            const dist = Math.sqrt(nodeX ** 2 + nodeY ** 2);

            if (dist > radius) {
              const angle = Math.atan2(nodeY, nodeX);
              node.x = Math.cos(angle) * radius;
              node.y = Math.sin(angle) * radius;
            }
          });
          */
        }}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const size = node.val;
          if (!size) return;

          const imgSize = size * 1.5;
          const iconUrl = getNodeIconUrl(node);
          const img = imageCacheRef.current[iconUrl];

          if (img && img.complete && img.naturalHeight !== 0) {
            try {
              ctx.drawImage(
                img,
                node.x - imgSize / 2,
                node.y - imgSize / 2,
                imgSize,
                imgSize
              );
            } catch (e) {
              console.error(`Error drawing image ${iconUrl} for node ${node.id}:`, e);
            }
          } else {
            ctx.beginPath();
            ctx.arc(node.x, node.y, size / 2, 0, 2 * Math.PI, false);
            ctx.fillStyle = node.color || '#fdba74';
            ctx.fill();
          }
        }}
      />

      <Sheet open={isSheetOpen}>
        {selectedNodeData && (
          <SheetContent
            onEscapeKeyDown={() => setIsSheetOpen(false)}
            onPointerDownOutside={() => setIsSheetOpen(false)}
            className="custom-scrollbar h-2/3 overflow-y-auto"
          >
            <SheetHeader>
              <SheetTitle className="flex w-72 items-center gap-2">
                {selectedNodeData?.label || 'Detalhes'}
              </SheetTitle>
              <button
                onClick={() => setIsSheetOpen(false)}
                className="absolute right-4 top-4 rounded-full bg-zinc-100 p-2 opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-secondary"
              >
                <X className="size-4" />
              </button>
            </SheetHeader>

            {isQueryLoading && (
              <div className="flex h-[200px] items-center justify-center">
                <Loader2 className="size-7 animate-spin" />
              </div>
            )}

            {queryData && (
              <div className="space-y-4 py-2">
                {selectedNodeData.type === 'Advogado' &&
                  queryData.advogados.map((data: any) => (
                    <div key={data.advogado_id} className="space-y-4">
                      <div className="space-x-2">
                        {console.log(data)}

                        {data.stakeholder && (
                          <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                            stakeholder
                          </span>
                        )}

                        {data.em_prospeccao && (
                          <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                            Em prospecção
                          </span>
                        )}

                        <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                          {selectedNodeData.type}
                        </span>
                      </div>

                      <Separator />

                      <div className="space-y-1">
                        <span className="font-medium">OAB</span>
                        <p className="text-sm text-muted-foreground">
                          {data.oab}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">CPF</span>
                        <p className="text-sm text-muted-foreground">
                          {formatCpfCnpj(data.cpf)}
                        </p>
                      </div>

                      <Separator />
                      <h2 className="font-medium">Detalhes de contato</h2>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">Instagram</span>
                          {(() => {
                            let id = '';
                            let tipo = '';
                            if (selectedNodeData.type === 'Empresa' && data.cnpj) {
                              id = data.cnpj;
                              tipo = 'empresa';
                            } else if (selectedNodeData.type === 'Pessoa' && data.cpf) {
                              id = data.cpf;
                              tipo = 'pessoa';
                            } else if (selectedNodeData.type === 'Advogado') {
                              if (data.cpf && data.cpf.trim() !== '' && data.cpf !== 'None') {
                                id = data.cpf;
                              } else if (data.oab && data.oab.trim() !== '' && data.oab !== 'None') {
                                id = data.oab;
                              }
                              tipo = 'advogado';
                            }
                            if (id && tipo) {
                              return (
                                <Link href={`/instagram-search/relacionados?id=${encodeURIComponent(id)}&type=${tipo}`} passHref legacyBehavior>
                                  <Button variant="outline" size="sm" className="ml-1">Buscar Relacionados</Button>
                                </Link>
                              );
                            }
                            return null;
                          })()}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {data.instagram !== 'None' ? data.instagram : 'Não informado'}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <span className="text-sm font-medium">LinkedIn</span>
                        <p className="text-sm text-muted-foreground">
                          {data.linkedin !== 'None'
                            ? data.linkedin
                            : 'Não informado'}
                        </p>
                      </div>
                    </div>
                  ))}

                {selectedNodeData.type === 'Escritorio' &&
                  queryData.escritorios.map((data: any) => (
                    <div key={data.escritorio_id} className="space-y-4">
                      <div className="space-x-2">
                        <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                          {selectedNodeData.type}
                        </span>

                        {data.stakeholder && (
                          <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                            stakeholder
                          </span>
                        )}

                        {data.em_prospeccao && (
                          <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                            Em prospecção
                          </span>
                        )}
                      </div>

                      <Separator />

                      <div className="space-y-1">
                        <span className="font-medium">Nome do Escritório</span>
                        <p className="text-sm text-muted-foreground">
                          {data.nome}
                        </p>
                      </div>
                      <Separator />
                      <h2 className="font-medium">Localização</h2>
                      <div className="space-y-1">
                        <span className="text-sm font-medium">Endereço</span>
                        <p className="text-sm text-muted-foreground">
                          {data.endereco || 'Não informado'}
                        </p>
                      </div>

                      <Separator />
                      <h2 className="font-medium">Detalhes de contato</h2>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">Instagram</span>
                          {(() => {
                            let id = '';
                            let tipo = '';
                            if (selectedNodeData.type === 'Empresa' && data.cnpj) {
                              id = data.cnpj;
                              tipo = 'empresa';
                            } else if ((selectedNodeData.type === 'Pessoa' || selectedNodeData.type === 'Advogado') && data.cpf) {
                              id = data.cpf;
                              tipo = selectedNodeData.type.toLowerCase();
                            }
                            if (id && tipo) {
                              return (
                                <Link href={`/instagram-search/relacionados?id=${encodeURIComponent(id)}&type=${tipo}`} passHref legacyBehavior>
                                  <Button variant="outline" size="sm" className="ml-1">Buscar Relacionados</Button>
                                </Link>
                              );
                            }
                            return null;
                          })()}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {data.instagram !== 'None' ? data.instagram : 'Não informado'}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <span className="text-sm font-medium">LinkedIn</span>
                        <p className="text-sm text-muted-foreground">
                          {data.linkedin !== 'None'
                            ? data.linkedin
                            : 'Não informado'}
                        </p>
                      </div>
                    </div>
                  ))}

                {selectedNodeData.type === 'Empresa' &&
                  queryData.empresas.map((data: any) => (
                    <div key={data.empresa_id} className="space-y-4">
                      <div className="space-x-2">
                        <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                          {selectedNodeData.type}
                        </span>

                        {data.stakeholder && (
                          <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                            stakeholder
                          </span>
                        )}

                        {data.em_prospecao && (
                          <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                            Em prospecção
                          </span>
                        )}
                      </div>

                      <Separator />

                      {selectedNodeData.documento && (
                        <div className="space-y-1">
                          <span className="font-medium">CNPJ</span>
                          <p className="text-sm text-muted-foreground">
                            {formatCpfCnpj(data.cnpj)}
                          </p>
                        </div>
                      )}

                      <div className="space-y-1">
                        <span className="font-medium">Razão social</span>
                        <p className="text-sm text-muted-foreground">
                          {data.razao_social}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <span className="font-medium">Nome fantasia</span>
                        <p className="text-sm text-muted-foreground">
                          {data.nome_fantasia !== 'None'
                            ? data.nome_fantasia
                            : 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">Projeto</span>
                        <p className="text-sm text-muted-foreground">
                          {data.projeto || 'Não atribuído'}
                        </p>
                      </div>

                      <Separator />

                      <div className="space-y-1">
                        <span className="font-medium">Data de fundação</span>
                        <p className="text-sm text-muted-foreground">
                          {data.data_fundacao !== 'None'
                            ? data.data_fundacao
                            : 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">CNAE</span>
                        <p className="text-sm text-muted-foreground">
                          {data.cnae || 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">Descrição CNAE</span>
                        <p className="text-sm text-muted-foreground">
                          {data.descricao_cnae || 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">Porte da empresa</span>
                        <p className="text-sm text-muted-foreground">
                          {data.porte || 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">Tipo de CNPJ</span>
                        <p className="text-sm text-muted-foreground">
                          {data.tipo_empresa || 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">
                          Faixa de funcionários
                        </span>
                        <p className="text-sm text-muted-foreground">
                          {data.faixa_funcionarios || 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">
                          Quantidade de funcionários
                        </span>
                        <p className="text-sm text-muted-foreground">
                          {data.quantidade_funcionarios || 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">
                          Faixa de faturamento
                        </span>
                        <p className="text-sm text-muted-foreground">
                          {data.faixa_faturamento || 'Não informado'}
                        </p>
                      </div>

                      <Separator />

                      <h2 className="font-medium">Detalhes de contato</h2>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">Instagram</span>
                          {(() => {
                            let id = '';
                            let tipo = '';
                            if (selectedNodeData.type === 'Empresa' && data.cnpj) {
                              id = data.cnpj;
                              tipo = 'empresa';
                            } else if ((selectedNodeData.type === 'Pessoa' || selectedNodeData.type === 'Advogado') && data.cpf) {
                              id = data.cpf;
                              tipo = selectedNodeData.type.toLowerCase();
                            }
                            if (id && tipo) {
                              return (
                                <Link href={`/instagram-search/relacionados?id=${encodeURIComponent(id)}&type=${tipo}`} passHref legacyBehavior>
                                  <Button variant="outline" size="sm" className="ml-1">Buscar Relacionados</Button>
                                </Link>
                              );
                            }
                            return null;
                          })()}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {data.instagram !== 'None' ? data.instagram : 'Não informado'}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <span className="text-sm font-medium">LinkedIn</span>
                        <p className="text-sm text-muted-foreground">
                          {data.linkedin !== 'None'
                            ? data.linkedin
                            : 'Não informado'}
                        </p>
                      </div>
                    </div>
                  ))}

                {selectedNodeData.type === 'Pessoa' &&
                  queryData.pessoas.map((data: any) => (
                    <div key={data.pessoa_id} className="space-y-4">
                      <div className="space-x-2">
                        <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                          {selectedNodeData.type}
                        </span>

                        {data.stakeholder && (
                          <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                            stakeholder
                          </span>
                        )}

                        {data.em_prospeccao && (
                          <span className="rounded-md border px-2 py-1 text-xs font-normal text-muted-foreground">
                            Em prospecção
                          </span>
                        )}
                      </div>

                      <Separator />

                      {selectedNodeData.documento && (
                        <div className="space-y-1">
                          <span className="font-medium">CPF</span>
                          <p className="text-sm text-muted-foreground">
                            {formatCpfCnpj(data.cpf)}
                          </p>
                        </div>
                      )}

                      <div className="space-y-1">
                        <span className="font-medium">Nome</span>
                        <p className="text-sm text-muted-foreground">
                          {data.firstname} {data.lastname}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">Sexo</span>
                        <p className="text-sm text-muted-foreground">
                          {data.sexo !== 'None' ? data.sexo : 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">Idade</span>
                        <p className="text-sm text-muted-foreground">
                          {data.idade !== 'None' ? data.idade : 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">Data de nascimento</span>
                        <p className="text-sm text-muted-foreground">
                          {data.data_nascimento !== 'None'
                            ? data.data_nascimento
                            : 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">Signo</span>
                        <p className="text-sm text-muted-foreground">
                          {data.signo !== 'None' ? data.signo : 'Não informado'}
                        </p>
                      </div>

                      <div className="space-y-1">
                        <span className="font-medium">Renda estimada</span>
                        <p className="text-sm text-muted-foreground">
                          {data.renda_estimada !== 'None'
                            ? `R$${data.renda_estimada}`
                            : 'Não informado'}
                        </p>
                      </div>

                      <Separator />

                      <h2 className="font-medium">Detalhes de contato</h2>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">Instagram</span>
                          {(() => {
                            let id = '';
                            let tipo = '';
                            if (selectedNodeData.type === 'Empresa' && data.cnpj) {
                              id = data.cnpj;
                              tipo = 'empresa';
                            } else if ((selectedNodeData.type === 'Pessoa' || selectedNodeData.type === 'Advogado') && data.cpf) {
                              id = data.cpf;
                              tipo = selectedNodeData.type.toLowerCase();
                            }
                            if (id && tipo) {
                              return (
                                <Link href={`/instagram-search/relacionados?id=${encodeURIComponent(id)}&type=${tipo}`} passHref legacyBehavior>
                                  <Button variant="outline" size="sm" className="ml-1">Buscar Relacionados</Button>
                                </Link>
                              );
                            }
                            return null;
                          })()}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {data.instagram !== 'None' ? data.instagram : 'Não informado'}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <span className="text-sm font-medium">LinkedIn</span>
                        <p className="text-sm text-muted-foreground">
                          {data.linkedin !== 'None'
                            ? data.linkedin
                            : 'Não informado'}
                        </p>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </SheetContent>
        )}
      </Sheet>

      {/* Painel de Controles da Simulação */}
      <div
        className={`absolute ${openControls ? 'right-4' : '-right-[320px]'} top-24 z-20 space-y-1 transition-all ease-in-out`}
        style={{ maxWidth: '320px' }}
      >
        <div className="relative w-full space-y-3 rounded-lg border bg-background p-4 shadow-lg max-h-[calc(100vh-10rem)] overflow-y-auto">
          <button
            type="button"
            title="Ajustes da Simulação"
            className="absolute -left-10 top-2 flex h-10 w-10 items-center justify-center rounded-s-lg border bg-background"
            onClick={() => setOpenControls(!openControls)}
          >
            {openControls ? (
              <ChevronsRight className="size-4" />
            ) : (
              <ChevronsLeft className="size-4" />
            )}
          </button>

          <h3 className="font-semibold text-lg mb-3">Ajustes da Simulação</h3>

          <div className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="chargeStrength" className="text-sm font-medium flex justify-between">
                Repulsão (Charge) <span>{chargeStrength.toFixed(2)}</span>
              </Label>
              <input
                type="range"
                id="chargeStrength"
                min={-100}
                max={0}
                step={1}
                value={chargeStrength}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setChargeStrength(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="distanceMax" className="text-sm font-medium flex justify-between">
                Alcance Repulsão (Max) <span>{distanceMax.toFixed(0)}</span>
              </Label>
              <input
                type="range"
                id="distanceMax"
                min={10}
                max={1000}
                step={10}
                value={distanceMax}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDistanceMax(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="linkStrength" className="text-sm font-medium flex justify-between">
                Força Link <span>{linkStrength.toFixed(2)}</span>
              </Label>
              <input
                type="range"
                id="linkStrength"
                min={0}
                max={1}
                step={0.01}
                value={linkStrength}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLinkStrength(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="linkDistance" className="text-sm font-medium flex justify-between">
                Distância Link <span>{linkDistance.toFixed(0)}</span>
              </Label>
              <input
                type="range"
                id="linkDistance"
                min={1}
                max={100}
                step={1}
                value={linkDistance}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLinkDistance(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="centerStrength" className="text-sm font-medium flex justify-between">
                Força Central <span>{centerStrength.toFixed(2)}</span>
              </Label>
              <input
                type="range"
                id="centerStrength"
                min={0}
                max={1}
                step={0.01}
                value={centerStrength}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCenterStrength(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="collideRadius" className="text-sm font-medium flex justify-between">
                Raio Colisão <span>{collideRadius.toFixed(0)}</span>
              </Label>
              <input
                type="range"
                id="collideRadius"
                min={1}
                max={20}
                step={1}
                value={collideRadius}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCollideRadius(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="alphaDecay" className="text-sm font-medium flex justify-between">
                Decaimento Alpha <span>{alphaDecay.toFixed(4)}</span>
              </Label>
              <input
                type="range"
                id="alphaDecay"
                min={0.001}
                max={0.1}
                step={0.001}
                value={alphaDecay}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAlphaDecay(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="velocityDecay" className="text-sm font-medium flex justify-between">
                Decaimento Velocidade <span>{velocityDecay.toFixed(2)}</span>
              </Label>
              <input
                type="range"
                id="velocityDecay"
                min={0.1}
                max={1.0}
                step={0.01}
                value={velocityDecay}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setVelocityDecay(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
