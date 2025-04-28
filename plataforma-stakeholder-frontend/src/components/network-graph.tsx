import {
  CSSProperties,
  FC,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react'

import { useSearchParams } from 'next/navigation'

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

import { MultiDirectedGraph } from 'graphology'

import louvain from 'graphology-communities-louvain'
import { schemeCategory10 } from 'd3-scale-chromatic'

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

// RE-ADD: Imports for D3 Hierarchy/Pack
import { hierarchy, pack } from 'd3-hierarchy'
import ForceAtlas2Layout from 'graphology-layout-forceatlas2/worker'

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

const sigmaSettings = {
  allowInvalidContainer: true,
  renderEdgeLabels: true,
  nodeProgramClasses: { image: NodeImageProgram },
  defaultNodeType: 'image',
  defaultEdgeType: 'straight',
  labelDensity: 0.05,
  labelFont: 'Lato, sans-serif',
  zIndex: true,
  labelGridCellSize: 60,
  labelRenderedSizeThreshold: 30,
  enableEdgeLabels: true,
  scalingMode: 'outside',
}

type GraphEventsProps = {
  onNodeClick: (nodeId: string) => void
}

const GraphEvents: FC<GraphEventsProps> = ({ onNodeClick }) => {
  console.log('[GraphEvents] Rendering');
  const registerEvents = useRegisterEvents()
  const sigma = useSigma()
  const draggedNode = useRef<string | null>(null)
  const isDragging = useRef(false)
  const startMousePosition = useRef<{ x: number; y: number } | null>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  useEffect(() => {
    console.log('[GraphEvents] useEffect setup starting');
    const graph = sigma.getGraph()
    const DRAG_THRESHOLD = 3

    const highlightNodeEdges = (nodeId: string) => {
      graph.forEachEdge((edge) => {
        graph.setEdgeAttribute(edge, 'color', '#cccccc')
        graph.setEdgeAttribute(edge, 'size', 1)
      })

      graph.forEachEdge((edge, _, source, target) => {
        if (source === nodeId || target === nodeId) {
          graph.setEdgeAttribute(edge, 'color', '#f43f5e')
          graph.setEdgeAttribute(edge, 'size', 1)
        }
      })

      sigma.refresh()
    }

    registerEvents({
      downNode: (e) => {
        draggedNode.current = e.node
        startMousePosition.current = { x: e.event.x, y: e.event.y }
        isDragging.current = false
      },
      mousemovebody: (e) => {
        if (!draggedNode.current || !startMousePosition.current) return

        const dx = Math.abs(e.x - startMousePosition.current.x)
        const dy = Math.abs(e.y - startMousePosition.current.y)
        const distance = Math.sqrt(dx * dx + dy * dy)

        if (distance > DRAG_THRESHOLD) {
          isDragging.current = true
          const pos = sigma.viewportToGraph(e)
          graph.setNodeAttribute(draggedNode.current, 'x', pos.x)
          graph.setNodeAttribute(draggedNode.current, 'y', pos.y)
          e.preventSigmaDefault()
          e.original.preventDefault()
          e.original.stopPropagation()
        }
      },
      mouseup: () => {
        if (!isDragging.current && draggedNode.current) {
          const nodeId = draggedNode.current
          if (selectedNode === nodeId) {
            graph.forEachEdge((edge) => {
              graph.setEdgeAttribute(edge, 'color', '#cccccc')
              graph.setEdgeAttribute(edge, 'size', 1)
            })
            setSelectedNode(null)
          } else {
            highlightNodeEdges(nodeId)
            setSelectedNode(nodeId)
            onNodeClick(nodeId)
          }
          sigma.refresh()
        }
        draggedNode.current = null
        startMousePosition.current = null
        isDragging.current = false
      },
      clickStage: () => {
        graph.forEachEdge((edge) => {
          graph.setEdgeAttribute(edge, 'color', '#cccccc')
          graph.setEdgeAttribute(edge, 'size', 1)
        })
        setSelectedNode(null)
        sigma.refresh()
      },
    })
    console.log('[GraphEvents] useEffect setup complete');
  }, [registerEvents, sigma, onNodeClick, selectedNode])

  return null
}

interface NodePosition {
  x: number;
  y: number;
}

interface MyGraphComponentProps {
  clusters: NetworkGraphProps['clusters'];
  onProgressUpdate: (progress: number) => void;
  onLayoutComplete: () => void;
}

// RE-ADD D3 Hierarchy Interfaces
interface HierarchyLeafNode {
  name: string; // Node ID or Community ID
  value: number; // Size for packing
  communityId?: string | number;
}
interface HierarchyCommunityNode {
  name: string; // Community ID (prefixed)
  children: HierarchyLeafNode[];
  communityId?: string | number;
}
interface HierarchyRootNode {
  name: string; // Should be 'root'
  children: HierarchyLeafNode[] | HierarchyCommunityNode[];
}

const MyGraph: FC<MyGraphComponentProps> = ({
  clusters,
  onProgressUpdate,
  onLayoutComplete,
}) => {
  console.log('@@@ MyGraph component BODY rendering (Hybrid: Pack Communities + Force Inside) @@@');

  const loadGraph = useLoadGraph();
  const layoutRef = useRef<ForceAtlas2Layout | null>(null);

  const stableLoadGraph = useCallback<
    (graph: MultiDirectedGraph, fa2Running?: boolean) => void
  >(
    (graph, fa2Running = false) => {
      console.log('@@@ stableLoadGraph called @@@');
      if (loadGraph) {
        try {
          loadGraph(graph);
          console.log('@@@ stableLoadGraph: Graph loaded successfully @@@');
          if (!fa2Running) {
            onLayoutComplete();
          }
        } catch (error) {
          console.error("@@@ stableLoadGraph: Error loading graph into Sigma:", error);
          onProgressUpdate(-1);
        }
      } else {
        console.error('loadGraph function is not available when trying to load!');
        onProgressUpdate(-1);
      }
    },
    [loadGraph, onLayoutComplete, onProgressUpdate],
  );

  console.log('@@@ MyGraph: Defining useEffect for graph loading (Hybrid Layout) @@@');
  useEffect(() => {
    console.log('MyGraph useEffect TRIGGERED (Hybrid Layout)');
    let isCancelled = false;

    if (!clusters || clusters.length === 0) {
      console.log('No clusters to render, exiting useEffect');
      return;
    }

    const graph = new MultiDirectedGraph();
    console.log('Created new MultiDirectedGraph');
    const nodeSet = new Set<string>();
    const nodeInfoMap = new Map<string, { type: string; root: boolean }>();
    const processedEdges = new Set<string>();
    const nodeCommunityCenter = new Map<string, { packCenterX: number, packCenterY: number }>();

    console.log('Starting node processing');
    clusters.forEach((cluster) => {
      cluster.nodes.forEach((node) => {
        if (!nodeSet.has(node.id)) {
          let imageUrl = '/icons/pessoa.png';
          if (node.stakeholder) { imageUrl = '/icons/stakeholder2.png'; }
          else if (node.matched) { imageUrl = '/icons/stakeholder-matched.png'; }
          else if (node.type === 'Empresa') imageUrl = '/icons/empresa.png';
          else if (node.type === 'Socio') imageUrl = '/icons/socio.png';
          else if (node.type === 'Advogado') imageUrl = '/icons/advogado.png';
          else if (node.type === 'Pessoa') imageUrl = '/icons/pessoa.png';

          const initialX = Math.random() * 1000;
          const initialY = Math.random() * 1000;
          graph.addNode(node.id, {
            label: node.label,
            color: '#9ca3af',
            image: imageUrl,
            imageScale: 0.2,
            x: initialX, y: initialY,
            fixed: false
          });
          nodeSet.add(node.id);
          nodeInfoMap.set(node.id, { type: node.type, root: node.root });
        }
      });
    });
    console.log(`[MyGraph] Node Processing COMPLETE. Processed: ${graph.order} unique nodes.`);

    console.log('Starting edge processing');
    clusters.forEach((cluster) => {
      cluster.links.forEach((link) => {
        const edgeKey = `${link.source}_${link.target}`;
        const reverseEdgeKey = `${link.target}_${link.source}`;
        if (graph.hasNode(link.source) && graph.hasNode(link.target)) {
          if (!processedEdges.has(edgeKey) && !processedEdges.has(reverseEdgeKey) && !graph.hasEdge(link.source, link.target)) {
            const edgeAttributes = { label: link.label || 'Tipo de Ligação', color: '#cccccc', size: 0.5, type: 'line' };
            try {
              graph.addEdgeWithKey(edgeKey, link.source, link.target, edgeAttributes);
              processedEdges.add(edgeKey);
            } catch (e) {
              console.warn(`[MyGraph] Error adding edge ${edgeKey}:`, e);
            }
          }
        }
      });
    });
    console.log(`[MyGraph] Edge Processing COMPLETE. Edges: ${graph.size}`);

    if (graph.order === 0) {
      console.warn("Graph has no nodes after processing.");
      stableLoadGraph(graph);
      return;
    }

    console.log('Starting Louvain community detection...');
    let communitiesMap = new Map<string | number, string[]>();
    try {
      (louvain as any).assign(graph, { nodeCommunityAttribute: 'community' });
      graph.forEachNode((nodeId, attrs) => {
        const communityId = attrs.community ?? '__no_community__';
        if (!communitiesMap.has(communityId)) {
          communitiesMap.set(communityId, []);
        }
        communitiesMap.get(communityId)?.push(nodeId);
      });
      console.log(`Louvain detected ${communitiesMap.size} communities.`);
    } catch (error) {
      console.error('Error during Louvain detection:', error);
      communitiesMap = new Map();
    }

    console.log('Calculating community areas with D3 Pack...');
    const communityPositions = new Map<string | number, { packCenterX: number, packCenterY: number, packRadius: number }>();
    try {
      onProgressUpdate(10);
      const packHierarchyData: HierarchyRootNode = {
        name: 'root_community_packer',
        children: Array.from(communitiesMap.entries()).map(([communityId, nodesInCommunity]): HierarchyLeafNode => ({
          name: `community_${communityId}`,
          value: nodesInCommunity.length || 1,
          communityId: communityId,
        }))
      };
      onProgressUpdate(20);

      const PACK_COMMUNITY_DIAMETER = 10000;
      const rootCommunityPacker: any = hierarchy(packHierarchyData)
        .sum((d: any) => d.value || 0);

      const communityPackLayout = pack<any>()
        .size([PACK_COMMUNITY_DIAMETER, PACK_COMMUNITY_DIAMETER])
        .padding(150);

      const packedCommunitiesRoot: any = communityPackLayout(rootCommunityPacker);
      onProgressUpdate(30);

      packedCommunitiesRoot.leaves().forEach((leaf: any) => {
        const communityId = leaf.data.communityId;
        if (communityId !== undefined && typeof leaf.x === 'number' && typeof leaf.y === 'number' && typeof leaf.r === 'number') {
          const packCenterX = leaf.x - PACK_COMMUNITY_DIAMETER / 2;
          const packCenterY = leaf.y - PACK_COMMUNITY_DIAMETER / 2;
          communityPositions.set(communityId, { packCenterX, packCenterY, packRadius: leaf.r });
          communitiesMap.get(communityId)?.forEach(nodeId => {
            nodeCommunityCenter.set(nodeId, { packCenterX, packCenterY });
          });
        } else {
          console.warn(`Community ${communityId} could not be packed.`);
          communitiesMap.get(communityId)?.forEach(nodeId => {
            nodeCommunityCenter.set(nodeId, { packCenterX: 0, packCenterY: 0 });
          });
        }
      });
      console.log(`Calculated positions for ${communityPositions.size} communities.`);
      onProgressUpdate(40);

    } catch (error) {
      console.error('Error during D3 Community Packing:', error);
      graph.forEachNode(nodeId => nodeCommunityCenter.set(nodeId, { packCenterX: 0, packCenterY: 0 }));
      onProgressUpdate(40);
    }

    console.log('Placing nodes at relative center (0,0) for FA2...');
    graph.forEachNode(nodeId => {
      graph.setNodeAttribute(nodeId, 'x', 0);
      graph.setNodeAttribute(nodeId, 'y', 0);
    });
    onProgressUpdate(50);

    console.log('Starting ForceAtlas2 for internal community layout...');
    if (layoutRef.current) {
      layoutRef.current.stop();
    }

    const fa2InternalSettings = {
      linLogMode: true,
      outboundAttractionDistribution: true,
      adjustSizes: true,
      edgeWeightInfluence: 1,
      scalingRatio: 5,
      strongGravityMode: true,
      gravity: 15,
      slowDown: 1,
      barnesHutOptimize: graph.order > 500,
      barnesHutTheta: 0.6,
    };

    layoutRef.current = new ForceAtlas2Layout(graph, {
      settings: fa2InternalSettings,
      getEdgeWeight: 'weight'
    });

    const maxInternalIterations = 150;
    layoutRef.current.start();
    onProgressUpdate(60);

    let progressInterval: NodeJS.Timeout | null = null;
    let completionTimeout: NodeJS.Timeout | null = null;
    const estimatedInternalDurationMs = maxInternalIterations * 15;
    const startTime = Date.now();

    progressInterval = setInterval(() => {
      if (isCancelled) {
        if (progressInterval) clearInterval(progressInterval);
        return;
      }
      const elapsedTime = Date.now() - startTime;
      const progress = Math.min(90, 60 + (elapsedTime / estimatedInternalDurationMs) * 30);
      onProgressUpdate(progress);
    }, 100);

    completionTimeout = setTimeout(() => {
      if (isCancelled) return;
      if (progressInterval) clearInterval(progressInterval);
      progressInterval = null;

      console.log(`Internal FA2 estimated duration reached (${estimatedInternalDurationMs}ms). Stopping layout.`);
      layoutRef.current?.stop();

      console.log("Translating nodes to final packed positions...");
      graph.forEachNode((nodeId) => {
        const center = nodeCommunityCenter.get(nodeId);
        const relativeX = graph.getNodeAttribute(nodeId, 'x');
        const relativeY = graph.getNodeAttribute(nodeId, 'y');
        if (center && typeof relativeX === 'number' && typeof relativeY === 'number') {
          graph.setNodeAttribute(nodeId, 'x', center.packCenterX + relativeX);
          graph.setNodeAttribute(nodeId, 'y', center.packCenterY + relativeY);
        } else {
          console.warn(`Node ${nodeId} missing center or relative coords for translation.`);
          if (typeof relativeX !== 'number' || typeof relativeY !== 'number') {
            graph.setNodeAttribute(nodeId, 'x', 0);
            graph.setNodeAttribute(nodeId, 'y', 0);
          }
        }
      });
      onProgressUpdate(95);

      console.log("Applying final node sizes...");
      graph.forEachNode((nodeId) => {
        const nodeInfo = nodeInfoMap.get(nodeId);
        const BASE_NODE_SIZE = 5;
        const ROOT_NODE_SIZE = 10;
        const targetSize = nodeInfo?.root ? ROOT_NODE_SIZE : BASE_NODE_SIZE;
        graph.setNodeAttribute(nodeId, 'size', targetSize);
      });
      console.log("Final sizes applied.");

      stableLoadGraph(graph, false);
      onProgressUpdate(100);

    }, estimatedInternalDurationMs);

    console.log(`[MyGraph] useEffect - END (Hybrid Layout).`);

    return () => {
      console.log('MyGraph useEffect CLEANUP running (Hybrid Layout)');
      isCancelled = true;
      if (progressInterval) clearInterval(progressInterval);
      if (completionTimeout) clearTimeout(completionTimeout);
      progressInterval = null;
      completionTimeout = null;
      if (layoutRef.current) {
        layoutRef.current.stop();
      }
      layoutRef.current = null;
    };
  }, [clusters, stableLoadGraph, onProgressUpdate, onLayoutComplete]);

  console.log('@@@ MyGraph: Returning null (Hybrid Layout) @@@');
  return null;
};

export const NetworkGraph: FC<
  NetworkGraphProps & { style?: CSSProperties }
> = ({ clusters, style }) => {
  console.log('NetworkGraph component rendering');
  const [layoutProgress, setLayoutProgress] = useState<number | null>(null);
  const [isLayoutComplete, setIsLayoutComplete] = useState(false);

  const handleProgressUpdate = useCallback((progress: number) => {
    setLayoutProgress(progress);
    if (progress === 100) {
    }
    if (progress === -1) {
      setIsLayoutComplete(false);
    }
  }, []);

  const handleLayoutComplete = useCallback(() => {
    console.log("@@@ Layout Complete signal received by Parent @@@");
    setLayoutProgress(100);
    setIsLayoutComplete(true);
  }, []);

  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [selectedNodeData, setSelectedNodeData] = useState<Nodes | null>(null);

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

  const handleNodeClick = useCallback((nodeId: string) => {
    console.log('Node clicked:', nodeId);
    const selected = clusters.flatMap((cluster) => cluster.nodes).find((node) => node.id === nodeId);
    setSelectedNodeData(selected || null);
    setIsSheetOpen(true);
  }, [clusters]);

  if (!clusters || clusters.length === 0) {
    return <div>Carregando ou sem dados para o grafo...</div>;
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh' }}>
      {layoutProgress !== null && layoutProgress >= 0 && layoutProgress < 100 && (
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', background: 'rgba(255, 255, 255, 0.9)', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', zIndex: 1001 }}>
          <div>Calculando layout do grafo...</div>
          <div style={{ width: '200px', height: '4px', background: '#eee', marginTop: '10px' }}>
            <div style={{ width: `${layoutProgress}%`, height: '100%', background: '#4CAF50', transition: 'width 0.1s linear' }} />
          </div>
          <div style={{ marginTop: '5px', fontSize: '12px' }}>{layoutProgress}%</div>
        </div>
      )}
      {layoutProgress === -1 && (
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 1001, background: 'rgba(255, 200, 200, 0.9)', padding: '20px', borderRadius: '8px', color: '#8B0000' }}>
          Erro ao calcular layout do grafo.
        </div>
      )}

      <SigmaContainer
        settings={sigmaSettings}
        style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          overflow: 'hidden',
          backgroundColor: '#fafafa',
          visibility: isLayoutComplete ? 'visible' : 'hidden',
          ...style,
        }}
      >
        <ControlsContainer position="bottom-right">
          <ZoomControl />
          <FullScreenControl />
        </ControlsContainer>

        <MyGraph
          clusters={clusters}
          onProgressUpdate={handleProgressUpdate}
          onLayoutComplete={handleLayoutComplete}
        />

        {isLayoutComplete && <GraphEvents onNodeClick={handleNodeClick} />}

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
                          <span className="text-sm font-medium">Instagram</span>
                          <p className="text-sm text-muted-foreground">
                            {data.instagram !== 'None'
                              ? data.instagram
                              : 'Não informado'}
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
                          <span className="text-sm font-medium">Instagram</span>
                          <p className="text-sm text-muted-foreground">
                            {data.instagram !== 'None'
                              ? data.instagram
                              : 'Não informado'}
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
                          <span className="text-sm font-medium">Instagram</span>
                          <p className="text-sm text-muted-foreground">
                            {data.instagram !== 'None'
                              ? data.instagram
                              : 'Não informado'}
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
                          <span className="text-sm font-medium">Instagram</span>
                          <p className="text-sm text-muted-foreground">
                            {data.instagram !== 'None'
                              ? data.instagram
                              : 'Não informado'}
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
      </SigmaContainer>
    </div>
  );
};
