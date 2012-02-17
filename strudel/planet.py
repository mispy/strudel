
class PlanetDisplay(object):
    ready = False

    @classmethod
    def setup(cls, app):
        cls.noisetex = app.loader.load3DTexture("texture/fbm_###.tif")
        cls.noisestage = TextureStage('noise')
        cls.layer1stage = TextureStage('layer1')
        cls.layer2stage = TextureStage('layer2')
        cls.layer3stage = TextureStage('layer3')
        cls.layer4stage = TextureStage('layer4')
        cls.texture_sets = {}

        layernames = ["layer1", "layer2", "layer3", "layer4"]
        stages = [cls.layer1stage, cls.layer2stage, cls.layer3stage, cls.layer4stage]
        texture_files = os.listdir("texture/")
        for filename in texture_files:
            name,ext = os.path.splitext(filename)
            if name.endswith( "layer1" ):
                paths = [ "texture/" + filename.replace("layer1",layer) for layer in layernames ]
                #print paths
                if all( os.path.exists( path ) for path in paths ):
                    setname = name.replace("layer1","").strip("_")
                    #print "Found layer set - %s"%setname
                    texture_set = [ (cls.noisestage,cls.noisetex) ]
                    for stage,path in zip(stages,paths):
                        tex = app.loader.loadTexture( path )
                        tex.setWrapU( Texture.WMClamp )
                        tex.setWrapV( Texture.WMClamp )
                        texture_set.append( (stage, tex) )
                    cls.texture_sets[setname] = texture_set

        cls.ready = True


    def __init__(self, app, planet):
        if not PlanetDisplay.ready: PlanetDisplay.setup(app)
        self.node = app.render.attachNewNode(SphereNode(subdivides=4))
        self.node.setShader(Shader.load("shader/starshader.cg"))
        self.cloudtime = 0.0
        self.seed = hash("fish")
        self.param_set = ParamSet(self.seed)

        self.compute_seed_param()
        for stage, tex in PlanetDisplay.texture_sets['sun_big']:
            self.node.setTexture(stage, tex)

        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.speed = 0.00000001
        self.lasttime = 0.0
        self.setup_shader_inputs()

    def compute_seed_param(self):
        rng = random.Random()
        rng.seed(self.seed)
        self.param_set.vectors["seed"] = Vec4(rng.random(), rng.random(), rng.random(), self.cloudtime)
        self.setup_shader_inputs()

    def setup_shader_inputs(self):
        for k, v in self.param_set.vectors.iteritems():
            self.node.setShaderInput(k, v)

    def tick(self, time):
        elapsed = time - self.lasttime
        self.lasttime = time
        self.cloudtime += elapsed * 0.02
        self.yaw += 360.0 * self.speed * elapsed
        self.node.setHpr(self.yaw, self.pitch, self.roll)
        self.compute_seed_param()
        self.setup_shader_inputs()

